import argparse
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Re tag docker image')
    parser.add_argument('image', type=str, help='Docker image')
    args = parser.parse_args()
    image: str = args.image
    if "tfx_py" in image:
        img_name, tag = image.split(":")
        py_ver = ".".join(img_name.strip("tfx_py").split())
        result_image = f"tfdv:{tag}-py{py_ver}"
    elif "tensorflow_py" in image:
        img_name, tag = image.split(":")
        py_ver = ".".join(img_name.strip("tensorflow_py").split())
        result_image = f"tensorflow:{tag}-py{py_ver}"
    else:
        raise ValueError(f"Invalid image: {image}")
    subprocess.run(["docker", "tag", image, result_image], stdout=None, stderr=None)
    subprocess.run(["docker", "image", "rm", image], stdout=None, stderr=None)
