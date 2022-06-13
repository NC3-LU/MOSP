import os
import subprocess

import pkg_resources

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
            version = pkg_resources.get_distribution("mosp").version
        except pkg_resources.DistributionNotFound:
            version = ""
    return version


__version__ = get_version()
