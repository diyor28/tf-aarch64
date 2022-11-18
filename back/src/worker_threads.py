import asyncio
import os
import queue
import re
import subprocess
import threading
import time
from typing import TextIO

from .build_model import Session, Build
from .conf import BUILDER_THREADS
from .utils import flat2dotted

logs_q = queue.Queue(maxsize=0)


def create_builders():
    lock = threading.Lock()
    builders: list[BuildScheduler] = []
    for i in range(BUILDER_THREADS):
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

    def __init__(self, commands: list[list[str]], log_file: TextIO, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
                    return

                try:
                    p.wait(timeout=5)
                    assert p.returncode == 0
                    return
                except subprocess.TimeoutExpired:
                    pass
        self.status = Build.Status.COMPLETED

    def run(self) -> None:
        self.status = Build.Status.BUILDING
        try:
            self.build()
        except AssertionError:
            self.status = Build.Status.FAILED


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

            commands = []

            for bazel_df in os.listdir("../../bazel"):
                bazel_ver = re.findall(r"bazel(\d\d)", bazel_df)[0]
                commands.append(["docker", "build", "-t", f"bazel:{flat2dotted(bazel_ver)}", "-f", f"../bazel/{bazel_df}", "../bazel/"])

            if build.type == Build.Type.TENSORFLOW:
                commands.append(["docker", "build", "-t", f"tensorflow_py{py_combined}:{build.package}", "-f", f"../tensorflow/Dockerfile_tf{pck_combined}_py{py_combined}", "../tensorflow/"])
                # command to copy produced wheels to host
                commands.append(["docker", "run", "-v", "~/volumes/builds:/builds", f"tensorflow_py{py_combined}:{build.package}", "cp", "-a", "/wheels/.", "/builds"])
            else:
                commands.append(["docker", "build", "-t", f"tfx_py{py_combined}:{build.package}", "-f", f"../tfx/Dockerfile_tfx{pck_combined}_py{py_combined}", "../tfx/"])
                # command to copy produced wheels to host
                commands.append(["docker", "run", "-v", "~/volumes/builds:/builds", f"tfx_py{py_combined}:{build.package}", "cp", "-a", "/wheels/.", "/builds"])

            builder = Builder(commands=commands, log_file=log_file)
            builder.start()
            while builder.is_alive():
                self.lock.acquire()
                build = session.query(Build).get(build.id)
                if build.status == Build.Status.CANCELLED:
                    builder.stop()
                    self.lock.release()
                    break
                self.lock.release()
                time.sleep(5)

            build.status = builder.status
            reader.stop()
            session.add(build)
            session.commit()


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
