import os
import subprocess
import threading
import time
from typing import TextIO

from .build_model import Session, Build
from .conf import BUILDER_THREADS
from .generate import tf_bazel_version, tfx_bazel_version, generate, build_command


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
    with open(filename, "r", errors='ignore') as file:
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
            build.update_status(Build.Status.BUILDING)
            session.add(build)
            session.commit()
            self.lock.release()

            log_file = open(f"./logs/{build.id}.txt", "w+", errors='ignore')

            commands = []

            if build.type == Build.Type.TENSORFLOW:
                bazel_ver = tf_bazel_version(build.package)
            else:
                bazel_ver = tfx_bazel_version(build.package)

            bazel_df = generate("bazel", bazel_ver)
            build_cmd, _ = build_command("bazel", bazel_ver, f"./build_files/{bazel_df}")
            commands.append(build_cmd.split(" "))

            if build.type == Build.Type.TENSORFLOW:
                docker_file = generate("tensorflow", build.package, build.python)
                build_cmd, image_name = build_command("tensorflow", build.package, f"./build_files/{docker_file}", build.python, use_cache=True)
                commands.append(build_cmd.split(" "))
            else:
                docker_file = generate("tfx", build.package, build.python)
                build_cmd, image_name = build_command("tfx", build.package, f"./build_files/{docker_file}", build.python, use_cache=True)
                commands.append(build_cmd.split(" "))

            # command to copy produced wheels to host
            commands.append(["docker", "run", "-v", "/tmp/tf_aarch64/volumes/builds:/builds", image_name, "cp", "-a", "/wheels/.", "/builds"])

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

            build.update_status(builder.status)
            session.add(build)
            session.commit()
