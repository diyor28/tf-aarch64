__all__ = ['tf_dockerfile', 'tfx_dockerfile', 'write_to_file', 'bazel_dockerfile']


def load_template(template: str) -> str:
    with open(f"../templates/{template}.template") as f:
        return "\n".join(f.readlines())


def gen_git_command(version: str) -> str:
    minor_version = version.split(".")[-1]
    if minor_version == "x":
        return f"git checkout r{version}"
    return f"git checkout tags/v{version}"


def tf_bazel_version(version: str) -> str:
    major_version = ".".join(version.split(".")[:-1])
    if major_version == "2.7":
        return "3.7"
    if major_version == "2.8":
        return "4.2"
    return "5.3"


def tf_numpy_version(version: str) -> str:
    if version in ["3.7", "3.8"]:
        return 'numpy<1.21.0'
    return 'numpy<1.24'


def tf_dockerfile(py_version: str, tf_version: str):
    bazel_version = tf_bazel_version(tf_version)
    numpy_version = tf_numpy_version(py_version)
    git_command = gen_git_command(tf_version)

    template_string = load_template("tensorflow")
    return template_string.format(git_command=git_command, bazel_version=bazel_version, numpy_version=numpy_version)


def tfx_bazel_version(tfx_version: str):
    return "4.2"


def tfx_dockerfile(py_version: str, tfx_version: str):
    major_version = ".".join(tfx_version.split(".")[:-1])
    bazel_version = tfx_bazel_version(tfx_version)
    git_command = gen_git_command(tfx_version)
    copy_arrow_command = ""
    if major_version in ["1.10"]:
        copy_arrow_command = "COPY arrow.BUILD ./third_party"
    copy_workspace_command = ""
    if major_version in ["1.4", "1.5", "1.6", "1.7"]:
        copy_workspace_command = "COPY WORKSPACE ./"

    template_string = load_template("tfx")
    return template_string.format(py_version=py_version, bazel_version=bazel_version, copy_arrow_comman=copy_arrow_command,
                                  git_command=git_command, copy_workspace_command=copy_workspace_command)


def bazel_dockerfile(bazel_version: str):
    if bazel_version == "3.7":
        bazel_version = "3.7.2"
    elif bazel_version == "4.2":
        bazel_version = "4.2.3"
    elif bazel_version == "5.3":
        bazel_version = "5.3.2"
    template_string = load_template("bazel")

    return template_string.format(bazel_version)


def write_to_file(template: str, path: str):
    with open(path, 'w') as f:
        f.write(template)
