import asyncio
import os
import queue
import subprocess
import threading
import time
from typing import TextIO

from conf import WHEELS_DIR
from store import Session, Build

logs_q = queue.Queue(maxsize=0)


def create_builders():
    lock = threading.Lock()
    builders: list[BuildScheduler] = []
    for i in range(5):
        b = BuildScheduler(lock)
        b.start()
        builders.append(b)
    return builders


class BaseThread(threading.Thread):
    _stopped: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stopped = False

    def stop(self):
        self._stopped = True


class Reader(BaseThread):
    def __init__(self, name: str, file: TextIO):
        super().__init__()
        self.name = name
        self.file = file

    def run(self) -> None:
        for line_n, line in follow(self.file):
            if self._stopped:
                break
            logs_q.put({"name": self.name, "line_number": line_n, "line": line})


readers: list[Reader] = []


class Builder(BaseThread):
    status: str

    def __init__(self, commands: list[list[str]], log_file: TextIO, lock: threading.Lock, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = lock
        self.commands = commands
        self.log_file = log_file
        self.status = Build.Status.PENDING

    def build(self):
        for cmd in self.commands:
            p = subprocess.Popen(cmd, stdout=self.log_file, stderr=self.log_file)
            while True:
                if self._stopped:
                    self.status = Build.Status.CANCELLED
                    p.terminate()
                    break
                try:
                    p.wait(timeout=5)
                    assert p.returncode == 0
                    break
                except subprocess.TimeoutExpired:
                    pass

    def run(self) -> None:
        self.status = Build.Status.BUILDING
        try:
            self.build()
        except Exception:
            self.status = Build.Status.FAILED
        self.status = Build.Status.COMPLETED


class BuildScheduler(BaseThread):
    def __init__(self, lock: threading.Lock):
        super().__init__()
        self.lock = lock

    def run(self) -> None:
        while True:
            if self._stopped:
                break
            self.lock.acquire()
            session = Session()
            build = session.query(Build).filter(Build.status == Build.Status.PENDING).first()
            if not build:
                self.lock.release()
                time.sleep(5)
                continue
            print(f"Found a job! Python: {build.python}, Package: {build.type}, Version: {build.package}")
            build.status = Build.Status.BUILDING
            session.add(build)
            session.commit()
            self.lock.release()

            pck_combined = ''.join(build.package.split('.'))
            py_combined = ''.join(build.python.split('.'))
            log_file = open(f"./logs/{build.filename}.txt", "w+")

            reader = Reader(build.filename, log_file)
            reader.start()
            readers.append(reader)

            if build.type == Build.Type.TENSORFLOW:
                build_cmd = ["docker", "build", "-t", f"tensorflow_py{py_combined}:{build.package}", "-f", f"../tensorflow/Dockerfile_tf{pck_combined}_py{py_combined}", "../tensorflow/"]
                cp_cmd = ["docker", "run", "-v", "~/volumes/builds:/builds", f"tensorflow_py{py_combined}:{build.package}", "cp", "-a", "/wheels/.", "/builds"]
            else:
                build_cmd = ["docker", "build", "-t", f"tfx_py{py_combined}:{build.package}", "-f", f"../tfx/Dockerfile_tfx{pck_combined}_py{py_combined}", "../tfx/"]
                cp_cmd = ["docker", "run", "-v", "~/volumes/builds:/builds", f"tfx_py{py_combined}:{build.package}", "cp", "-a", "/wheels/.", "/builds"]

            builder = Builder(commands=[build_cmd, cp_cmd], log_file=log_file, lock=self.lock)
            while True:
                self.lock.acquire()
                build = session.query(Build).get(build.id)
                if build.status == Build.Status.CANCELLED:
                    builder.stop()
                    break
                self.lock.release()
                if builder.is_alive():
                    time.sleep(5)
                else:
                    break

            build.status = builder.status
            session.add(build)
            session.commit()


def wheels_list() -> list[dict[str, str]]:
    wheel_files = [f for f in os.listdir(WHEELS_DIR) if os.path.isfile(os.path.join(WHEELS_DIR, f))]
    res = []
    for file in wheel_files:
        res.append({"name": file, "url": f"/builds/{file}"})
    return res


def get_filename(py_version: str, pck_version: str, pck_type: str):
    tf_combined = ''.join(pck_version.split('.'))
    py_combined = ''.join(py_version.split('.'))
    if pck_type == Build.Type.TFX:
        return f"tfx{tf_combined}_py{py_combined}"
    return f"tf{tf_combined}_py{py_combined}"


def follow(file: TextIO):
    while True:
        file.seek(0, 0)
        lines = file.readlines()
        for idx, line in enumerate(lines[-5:]):
            yield len(lines) + 5 + idx, line.strip()
        time.sleep(0.4)


async def get_log_updates():
    while True:
        try:
            yield logs_q.get(block=False)
        except queue.Empty:
            await asyncio.sleep(0.5)
