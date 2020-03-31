import os
import subprocess

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

__version__ = (
    os.environ.get("PKGVER")
    or subprocess.run(
        ["git", "-C", BASE_DIR, "describe", "--tags"], stdout=subprocess.PIPE
    )
    .stdout.decode()
    .strip()
)
