import re
import os
import glob

from .conf import WHEELS_DIR


def wheels_list() -> list[dict[str, str]]:
    wheel_files = [f for f in os.listdir(WHEELS_DIR) if os.path.isfile(os.path.join(WHEELS_DIR, f))]
    res = []
    for file in wheel_files:
        res.append({"name": file, "url": f"/builds/{file}"})
    return res


def flat2dotted(version: str):
    return '.'.join([version[0], version[1:]])


def dotted2flat(version: str):
    return ''.join(version.split('.'))


def list_versions(path: str, exp: str):
    result = []

    for _, df in scan_dockerfiles(path, exp).items():
        pkg_ver = df["version"]
        for m_ver in df["minor_versions"]:
            result.append(f"{pkg_ver}.{m_ver}")
        result.append(f"{pkg_ver}.x")
    return result


def scan_dockerfiles(path: str, exp: str) -> dict:
    result = {}
    df_files = glob.glob(path)
    for df in df_files:
        pkg_ver, minor_versions = re.findall(exp, os.path.basename(df))[0]
        pkg_ver = flat2dotted(pkg_ver)
        result[pkg_ver] = {
            "df": df,
            "version": pkg_ver,
            "minor_versions": minor_versions.split(",")
        }
    return result
