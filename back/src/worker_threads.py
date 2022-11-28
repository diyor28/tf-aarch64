import os
import re
import subprocess
import threading
import time
from typing import TextIO

from .build_model import Session, Build
from .conf import BUILDER_THREADS, TF_DF_REGEX, TFX_DF_REGEX
from .utils import flat2dotted, scan_dockerfiles

log_files = {}


def create_builders():
    lock = threading.Lock()
    builders: list[BuildScheduler] = []
    for i in range(BUILDER_THREADS):
        b = BuildScheduler(lock)
        b.start()
        builders.append(b)
    return builders


def get_logs(pk: str, n_lines: int = 15):
    logs = []
    filename = f"./logs/{pk}.txt"
    if not os.path.exists(filename):
        return []
    file = log_files.get(pk, open(filename, "r"))
    if not file:
        return []
    file.seek(0, 0)
    lines = file.readlines()
    for idx, line in enumerate(lines[-1 * n_lines:]):
        logs.append({"line_number": len(lines) + 5 + idx, "line": line.strip()})
    return logs


class BaseThread(threading.Thread):
    _stopped: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stopped = False

    def stop(self):
        self._stopped = True


class Builder(BaseThread):
    status: str

    def __init__(self, commands: list[list[str]], log_file: TextIO, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = commands
        self.log_file = log_file
        self.status = Build.Status.PENDING

    def build(self):
        for cmd in self.commands:
            cmd_str = " ".join(cmd)
            print(f"Builder: Running command \"{cmd_str}\"")
            p = subprocess.Popen(cmd, stdout=self.log_file, stderr=self.log_file)
            while True:
                if self._stopped:
                    print("Builder: Received a stop signal. Terminating process...")
                    self.status = Build.Status.CANCELLED
                    p.terminate()
                    return

                try:
                    p.wait(timeout=5)
                    if p.returncode != 0:
                        print(f"Builder: Command \"{cmd_str}\" return exit code {p.returncode}")
                    assert p.returncode == 0
                    break
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
            print(f"Job found. Python: {build.python}, Package: {build.type}, Version: {build.package}")
            build.status = Build.Status.BUILDING
            session.add(build)
            session.commit()
            self.lock.release()

            py_ver = build.python
            pkg_ver_split = build.package.split(".")
            pkg_minor_ver = pkg_ver_split[-1]
            pkg_major_ver = ".".join(pkg_ver_split[:-1])
            pkg_ver = ".".join(pkg_ver_split[:-1]) if pkg_minor_ver == "x" else build.package
            py_combined = ''.join(build.python.split('.'))
            build_args = ["--build-arg", f"PYTHON_VERSION={py_ver}", "--build-arg", f"MINOR_VERSION={pkg_minor_ver}"]
            log_file = open(f"./logs/{build.id}.txt", "w+")

            log_files[build.id] = log_file

            commands = []

            for bazel_df in os.listdir("../bazel"):
                bazel_ver = re.findall(r"bazel(\d\d)", bazel_df)[0]
                commands.append(["docker", "build", "-t", f"bazel:{flat2dotted(bazel_ver)}", "-f", f"../bazel/{bazel_df}", "../bazel/"])

            if build.type == Build.Type.TENSORFLOW:
                dfs_map = scan_dockerfiles("../tensorflow/Dockerfile*", TF_DF_REGEX)
                image_name = f"tensorflow_py{py_combined}:{pkg_ver}"
                docker_file = dfs_map[pkg_major_ver]["df"]
                commands.append(["docker", "build", "-t", image_name, "-f", docker_file, *build_args, "../tensorflow/"])
                # command to copy produced wheels to host
                commands.append(["docker", "run", "-v", "~/volumes/builds:/builds", image_name, "cp", "-a", "/wheels/.", "/builds"])
            else:
                dfs_map = scan_dockerfiles("../tfx/Dockerfile*", TFX_DF_REGEX)
                image_name = f"tfx_py{py_combined}:{pkg_ver}"
                docker_file = dfs_map[pkg_major_ver]["df"]
                commands.append(["docker", "build", "-t", image_name, "-f", docker_file, *build_args, "../tfx/"])
                # command to copy produced wheels to host
                commands.append(["docker", "run", "-v", "~/volumes/builds:/builds", image_name, "cp", "-a", "/wheels/.", "/builds"])

            print("Starting builder")
            builder = Builder(commands=commands, log_file=log_file)
            builder.start()
            while builder.is_alive():
                if self._stopped:
                    break
                self.lock.acquire()
                session = Session()
                build = session.query(Build).get(build.id)
                if build.status == Build.Status.CANCELLED:
                    builder.stop()
                    self.lock.release()
                    break
                self.lock.release()
                time.sleep(3)

            build.status = builder.status
            log_files.pop(build.id)
            session.add(build)
            session.commit()
