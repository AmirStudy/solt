#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

setup_requirements = ()

description = """Benchmark of the data augmentation libraries"""

setup(
    author="Aleksei Tiulpin",
    author_email="aleksei.tiulpin@oulu.fi",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    description="Benchmark of different data augmentation libraries",
    install_requires=open("requirements.txt").read(),
    license="MIT license",
    long_description=description,
    include_package_data=True,
    keywords="data augmentations, deeep learning",
    name="augbench",
    packages=find_packages(include=["augbench"]),
    setup_requires=setup_requirements,
    url="https://github.com/mipt-oulu/solt/benchmark",
    version="0.1.9",
    zip_safe=False,
)
