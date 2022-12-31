__all__ = ["tfx_bazel_version", "tf_bazel_version", "tf_dockerfile", "tfx_dockerfile", "bazel_dockerfile", "generate", "write_to_file", "build_command"]

import os
import typing

CLI_MODE = os.getenv("CLI", False)
if CLI_MODE:
    TEMPLATES_DIR = "./build_templates"
else:
    TEMPLATES_DIR = "../build_templates"


def build_command(pkg_type: str, pkg_ver: str, df_path: str, py_ver: typing.Optional[str] = None, use_cache=True) -> tuple[str, str]:
    py_ver_combined = "".join(py_ver.split(".")) if py_ver else ""
    context_path = os.path.join(TEMPLATES_DIR, "context")
    extra_args = []

    if pkg_type == "bazel":
        image_name = f"bazel:{pkg_ver}"
    elif pkg_type == "tensorflow":
        image_name = f"tensorflow_py{py_ver_combined}:{pkg_ver}"
        if use_cache:
            extra_args.append("--network=bazel-cache")
    elif pkg_type == "tfx":
        if use_cache:
            extra_args.append("--network=bazel-cache")
        image_name = f"tfx_py{py_ver_combined}:{pkg_ver}"
    else:
        raise ValueError(f"Unknown package type {pkg_type}")

    return " ".join(["docker", "buildx", "build", "--platform=linux/arm64", *extra_args, "-t", image_name, "-f", df_path, context_path]), image_name


def get_major_version(version: str) -> str:
    return ".".join(version.split(".")[:-1])


def load_template(template: str) -> str:
    with open(os.path.join(TEMPLATES_DIR, f"{template}.template")) as f:
        return "".join(f.readlines())


def gen_git_command(version: str) -> str:
    minor_version = version.split(".")[-1]
    if minor_version == "x":
        return f"git checkout r{get_major_version(version)}"
    return f"git checkout tags/v{version}"


def tf_use_cache_command(use_cache: bool):
    if not use_cache:
        return ""
    return "RUN echo $'\\nbuild --remote_cache=grpc://bazel-cache:9092' >> .bazelrc"


def tf_protobuf_command(version: str) -> str:
    major_version = get_major_version(version)
    if major_version == "2.8":
        return "RUN pip install protobuf==3.20.1"
    return ""


def tf_io_command(version: str) -> str:
    major_version = get_major_version(version)
    version_matrix = {
        "2.11": "0.29.0",
        "2.10": "0.27.0",
        "2.9": "0.26.0",
        "2.8": "0.25.0",
        "2.7": "0.24.0"
    }
    return f"RUN pip install --no-deps tensorflow-io=={version_matrix.get(major_version, '0.29.0')}"


def tf_bazel_version(version: str) -> str:
    major_version = get_major_version(version)
    if major_version == "2.7":
        return "3.7"
    if major_version == "2.8":
        return "4.2"
    return "5.3"


def tf_numpy_version(version: str) -> str:
    if version in ["3.7", "3.8"]:
        return 'numpy<1.21.0'
    return 'numpy<1.24'


def tf_dockerfile(py_version: str, tf_version: str, use_cache=False):
    bazel_version = tf_bazel_version(tf_version)
    numpy_version = tf_numpy_version(py_version)
    git_command = gen_git_command(tf_version)
    protobuf_command = tf_protobuf_command(tf_version)
    tensorflow_io_command = tf_io_command(tf_version)
    use_cache_command = tf_use_cache_command(use_cache)

    template_string = load_template("tensorflow")
    return template_string.format(git_command=git_command, py_version=py_version, bazel_version=bazel_version,
                                  numpy_version=numpy_version, protobuf_command=protobuf_command,
                                  tensorflow_io_command=tensorflow_io_command, use_cache_command=use_cache_command)


def tfx_bazel_version(tfx_version: str):
    return "4.2"


def tfx_dockerfile(py_version: str, tfx_version: str, use_cache=False):
    major_version = get_major_version(tfx_version)
    bazel_version = tfx_bazel_version(tfx_version)
    git_command = gen_git_command(tfx_version)
    copy_arrow_command = ""
    if major_version in ["1.10", "1.11", "1.12"]:
        copy_arrow_command = "COPY tfx/arrow.BUILD ./third_party"
    copy_workspace_command = ""
    if major_version in ["1.4", "1.5", "1.6", "1.7"]:
        copy_workspace_command = "COPY tfx/WORKSPACE ./"
    use_cache_command = tf_use_cache_command(use_cache)

    template_string = load_template("tfx")
    return template_string.format(py_version=py_version, bazel_version=bazel_version,
                                  tfdv_git_command=git_command,
                                  tfx_bsl_git_command=git_command,
                                  copy_arrow_command=copy_arrow_command, copy_workspace_command=copy_workspace_command,
                                  use_cache_command=use_cache_command)


def bazel_dockerfile(bazel_version: str):
    if bazel_version == "3.7":
        bazel_version = "3.7.2"
    elif bazel_version == "4.2":
        bazel_version = "4.2.3"
    elif bazel_version == "5.3":
        bazel_version = "5.3.2"
    template_string = load_template("bazel")

    return template_string.format(bazel_version=bazel_version)


def write_to_file(instructions: str, path: str):
    with open(path, 'w') as f:
        f.write(instructions)


def generate(pkg_type: str, pkg_ver: str, py_ver: typing.Optional[str] = None, **kwargs) -> str:
    pkg_ver_flat = "".join(pkg_ver.split("."))
    py_ver_flat = "".join(py_ver.split(".")) if py_ver else ""

    if pkg_type == "bazel":
        df_name = f"bazel_{pkg_ver_flat}"
        instructions = bazel_dockerfile(pkg_ver)
    elif pkg_type == "tensorflow":
        df_name = f"tf{pkg_ver_flat}_py{py_ver_flat}"
        instructions = tf_dockerfile(py_ver, pkg_ver, **kwargs)
    elif pkg_type == "tfx":
        df_name = f"tfx{pkg_ver_flat}_py{py_ver_flat}"
        instructions = tfx_dockerfile(py_ver, pkg_ver, **kwargs)
    else:
        raise ValueError(f"Unknown package type {pkg_type}")

    write_to_file(instructions, os.path.join("./build_files", df_name))
    return df_name
