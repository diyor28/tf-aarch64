import os

WHEELS_DIR = os.getenv("WHEELS_DIR")
BUILDER_THREADS = int(os.getenv("BUILDER_THREADS", 6))

TF_DF_REGEX = r"tf(\d+)\((.+)\)"
TFX_DF_REGEX = r"tfx(\d+)\((.+)\)"
