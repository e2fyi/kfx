#!/usr/bin/env python
# noqa
# pylint: skip-file
"""The setup script."""

from setuptools import setup

with open("requirements.txt", "r") as filein:
    requirements = filein.readlines()

with open("requirements-dev.txt", "r") as filein:
    requirements_dev = filein.readlines()

with open("version.txt", "r") as filein:
    version = filein.read()

with open("README.md", "r") as filein:
    readme = filein.read()

setup_requirements: list = [
    "setuptools >= 41.0.0",
    "wheel >= 0.26",
]

setup(
    author="eterna2",
    author_email="eterna2@hotmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Extensions for kubeflow pipeline sdk.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/e2fyi/kfx",
    include_package_data=True,
    package_data={"": ["version.txt", "requirements.txt", "requirements-dev.txt"]},
    keywords="kfx,kubeflow,pipelines,contrib,sdk",
    name="kfx",
    packages=["kfx.dsl", "kfx.vis"],
    setup_requires=setup_requirements,
    python_requires=">=3.6",
    install_requires=requirements,
    tests_require=requirements_dev,
    version=version,
)
