import io
import os
import subprocess

from setuptools import find_packages
from setuptools import setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

ver = os.environ.get("PKGVER") or subprocess.run(['git', 'describe', '--tags'],
      stdout=subprocess.PIPE).stdout.decode().strip()

setup(
    name='MOSP',
    version=ver,
    url='https://github.com/CASES-LU/MOSP',
    license='AGPL-3.0',
    author = 'Cédric Bonhomme',
    author_email='cedric@cedricbonhomme.org',
    description='A platform for creating, editing and sharing JSON objects.',
    long_description_content_type='text/markdown',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['flask'],
    extras_require={'test': ['pytest', 'coverage']},
)
