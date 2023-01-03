import os

WHEELS_DIR = os.getenv("WHEELS_DIR", "/app/builds")
BUILDER_THREADS = int(os.getenv("BUILDER_THREADS", 6))
USE_CACHE = os.getenv("USE_CACHE", "True") == "True"
