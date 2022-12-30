import argparse
from src.generate import tf_dockerfile, tfx_dockerfile, bazel_dockerfile, write_to_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Dockerfile to build tensorflow, tfx or bazel')

    parser.add_argument('package', type=str, choices=['bazel', 'tensorflow', 'tfx'], help='Which package to generate Dockerfile for')
    parser.add_argument('-v', '--version', help='Pacakge version to generate Dockerfile for: e.g. 2.7.3')
    parser.add_argument('-py', '--python', help='Python version to generate Dockerfile for: e.g. 3.8')
    parser.add_argument('path', help='Where to save generated Dockerfile: e.g. ./dockerfiles/Dockerfile_tf37_py38')

    args = parser.parse_args()

    instructions = ""
    if args.package == "tensorflow":
        instructions = tf_dockerfile(args.python, args.version)
    elif args.package == "tfx":
        instructions = tfx_dockerfile(args.python, args.version)
    elif args.package == "bazel":
        instructions = bazel_dockerfile(args.version)

    write_to_file(instructions, args.path)
