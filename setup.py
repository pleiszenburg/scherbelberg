# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    setup.py: Used for package distribution

    Copyright (C) 2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from setuptools import (
    find_packages,
    setup,
)
import ast
import os

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# List all versions of Python which are supported
python_minor_min = 8
python_minor_max = 9
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
def get_version(code):
    tree = ast.parse(code)
    for item in tree.body:
        if not isinstance(item, ast.Assign):
            continue
        if len(item.targets) != 1:
            continue
        if item.targets[0].id != "__version__":
            continue
        return item.value.s


with open(os.path.join(SRC_DIR, "scherbelberg", "__init__.py"), "r", encoding="utf-8") as f:
    __version__ = get_version(f.read())

# Requirements
base_require = ["click", "hcloud", "pyyaml", "typeguard",]
extras_require = {
    "base": base_require,
    "dev": ["black", "python-language-server[all]", "setuptools", "sphinx", "sphinx_rtd_theme", "twine", "wheel",],
}
extras_require["all"] = list(
    {rq for target in extras_require.keys() for rq in extras_require[target]}
)

# Install package
setup(
    name="scherbelberg",
    packages=find_packages(SRC_DIR),
    package_dir={"": SRC_DIR},
    version=__version__,
    description="HPC cluster deployment and management for the Hetzner Cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sebastian M. Ernst",
    author_email="ernst@pleiszenburg.de",
    url="https://github.com/pleiszenburg/scherbelberg",
    download_url="https://github.com/pleiszenburg/scherbelberg/archive/v%s.tar.gz"
    % __version__,
    license="BSD",
    keywords=["HPC", "cluster", "dask"],
    scripts=[],
    include_package_data=True,
    python_requires=">=3.{MINOR:d}".format(MINOR=python_minor_min),
    setup_requires=[],
    install_requires=base_require,
    extras_require=extras_require,
    zip_safe=False,
    entry_points={"console_scripts": ["scherbelberg = scherbelberg._cli:cli",],},
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
