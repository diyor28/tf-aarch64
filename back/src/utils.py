import os

from .conf import WHEELS_DIR


def wheels_list() -> list[dict[str, str]]:
    wheel_files = [f for f in os.listdir(WHEELS_DIR) if os.path.isfile(os.path.join(WHEELS_DIR, f))]
    res = []
    for file in wheel_files:
        res.append({"name": file, "url": f"/builds/{file}"})
    return res


def flat2dotted(version: str):
    return '.'.join(version.split(''))


def dotted2flat(version: str):
    return ''.join(version.split('.'))
