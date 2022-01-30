# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    setup.py: Used for package distribution

    Copyright (C) 2021-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the BSD 3-Clause License
("License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://github.com/pleiszenburg/scherbelberg/blob/master/LICENSE
Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os

from setuptools import (
    find_packages,
    setup,
)

from docs.source.version import get_version

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# List all versions of Python which are supported
python_minor_min = 8
python_minor_max = 10
confirmed_python_versions = [
    "Programming Language :: Python :: 3.{MINOR:d}".format(MINOR=minor)
    for minor in range(python_minor_min, python_minor_max + 1)
]

# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    long_description = f.read()

# Define source directory (path)
SRC_DIR = "src"

# Version
version = get_version()

# Requirements
base_require = [
    "click",
    "dask",
    "hcloud",
    "pyyaml",
    "typeguard",
]
extras_require = {
    "base": base_require,
    "dev": [
        "black",
        "myst-parser",
        "python-lsp-server[all]",
        "setuptools",
        "sphinx",
        "sphinx-click",
        "sphinx_rtd_theme",
        "sphinx-autodoc-typehints",
        "twine",
        "wheel",
    ],
}
extras_require["all"] = list(
    {rq for target in extras_require.keys() for rq in extras_require[target]}
)

# Install package
setup(
    name="scherbelberg",
    packages=find_packages(SRC_DIR),
    package_dir={"": SRC_DIR},
    version=version,
    description="HPC cluster deployment and management for the Hetzner Cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sebastian M. Ernst",
    author_email="ernst@pleiszenburg.de",
    url="https://github.com/pleiszenburg/scherbelberg",
    download_url=f"https://github.com/pleiszenburg/scherbelberg/archive/v{version:s}.tar.gz",
    license="BSD",
    keywords=["HPC", "cluster", "dask"],
    scripts=[],
    include_package_data=True,
    python_requires=">=3.{MINOR:d}".format(MINOR=python_minor_min),
    setup_requires=[],
    install_requires=base_require,
    extras_require=extras_require,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "scherbelberg = scherbelberg._cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ]
    + confirmed_python_versions
    + [
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: System :: Clustering",
        "Topic :: Scientific/Engineering",
        "Topic :: System",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
