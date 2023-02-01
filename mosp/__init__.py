import importlib
import os
import subprocess
from importlib.metadata import PackageNotFoundError


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_version():
    if os.getenv("MOSP_VERSION", False):
        return os.getenv("MOSP_VERSION", "")

    version = (
        os.environ.get("PKGVER")
        or subprocess.run(
            ["git", "-C", BASE_DIR, "describe", "--tags"], stdout=subprocess.PIPE
        )
        .stdout.decode()
        .strip()
    ) or ""
    if not version:
        try:
            version = "v" + importlib.metadata.version("mosp")
        except PackageNotFoundError:
            version = ""
    return version


__version__ = get_version()
