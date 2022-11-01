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
    builders: list[Builder] = []
    for i in range(5):
        b = Builder(lock)
        b.start()
        builders.append(b)
    return builders


class BaseThread(threading.Thread):
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
    def __init__(self, lock: threading.Lock):
        super().__init__()
        self.lock = lock
        self._stopped = False

    def stop(self):
        self._stopped = True

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

            try:
                if build.type == Build.Type.TENSORFLOW:
                    p = subprocess.Popen(["docker", "build", "-t", f"tensorflow_py{py_combined}:{build.package}", "-f", f"../tensorflow/Dockerfile_tf{pck_combined}_py{py_combined}", "."], stdout=log_file, stderr=log_file)
                    p.wait()
                    assert p.returncode == 0

                    p = subprocess.Popen(["docker", "run", "-v", "~/volumes/test:/builds", f"tensorflow_py{py_combined}:{build.package}", "cp", "-a", "/wheels/.", "/builds"], stdout=log_file, stderr=log_file)
                    p.wait()
                    assert p.returncode == 0

                if build.type == Build.Type.TFX:
                    p = subprocess.Popen(["docker", "build", "-t", f"tfx_py{py_combined}:{build.package}", "-f", f"../tfx/Dockerfile_tfx{pck_combined}_py{py_combined}", "."], stdout=log_file, stderr=log_file)
                    p.wait()
                    assert p.returncode == 0

                    p = subprocess.Popen(["docker", "run", "-v", "~/volumes/test:/builds", f"tfx_py{py_combined}:{build.package}", "cp", "-a", "/wheels/.", "/builds"], stdout=log_file, stderr=log_file)
                    p.wait()
                    assert p.returncode == 0

                build.status = Build.Status.COMPLETED
            except AssertionError:
                build.status = Build.Status.FAILED

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
    if pck_type == Build.Type.TFX_BSL:
        return f"tfxbsl{tf_combined}_py{py_combined}"
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
