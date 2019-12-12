import io

from setuptools import find_packages
from setuptools import setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="MOSP",
    version="0.9.0",
    url="https://github.com/CASES-LU/MOSP",
    license="AGPL",
    maintainer="Cédric Bonhomme",
    author_email='cedric@cedricbonhomme.org',
    maintainer_email="",
    description="A platform for creating, editing and sharing JSON objects.",
    long_description_content_type='text/markdown',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"],
    extras_require={"test": ["pytest", "coverage"]},
)
