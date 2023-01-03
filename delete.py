import subprocess

versions = ["2.7.0", "2.7.1", "2.7.2", "2.7.3", "2.7.4",
            "2.8.0", "2.8.1", "2.8.2", "2.8.3", "2.8.4",
            "2.9.0", "2.9.1", "2.9.2", "2.9.3",
            "2.10.0", "2.10.1"]

if __name__ == '__main__':
    for v in versions:
        subprocess.run(["docker", "image", "rm", f"diyor28/tensorflow:{v}-py38"], stderr=None, stdout=None)
