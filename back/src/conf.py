import os

WHEELS_DIR = os.getenv("WHEELS_DIR", "/app/builds")
BUILDER_THREADS = int(os.getenv("BUILDER_THREADS", 6))
