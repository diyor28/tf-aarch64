import os
from src.build_model import Base, eng

if __name__ == "__main__":
    if os.path.exists("./data/data.db"):
        print("data.db already exists, skipping...")
        exit(0)
    Base.metadata.create_all(eng)
