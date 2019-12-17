import os
import subprocess

__version__ = (
    os.environ.get("PKGVER")
    or subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode()
    .strip()
)
