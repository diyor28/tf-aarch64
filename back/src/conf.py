import os

WHEELS_DIR = os.getenv("WHEELS_DIR")
BUILDER_THREADS = int(os.getenv("BUILDER_THREADS", 6))
