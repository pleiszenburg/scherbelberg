# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    docs/source/conf.py: Docs configuration

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

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

# sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from docs.source.version import get_version


# -- Project information -----------------------------------------------------

project = "scherbelberg"
author = "Sebastian M. Ernst"
copyright = f"2021-2022 {author:s}"

# The full version, including alpha/beta/rc tags
release = get_version()


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Values to pass into the template engine's context for all pages.
html_context = {
    "sidebar_external_links_caption": "Links",
    "sidebar_external_links": [
        # ('<i class="fa fa-rss fa-fw"></i> Blog', 'https://www.000'),
        (
            '<i class="fa fa-github fa-fw"></i> Source Code',
            "https://github.com/pleiszenburg/scherbelberg",
        ),
        (
            '<i class="fa fa-bug fa-fw"></i> Issue Tracker',
            "https://github.com/pleiszenburg/scherbelberg/issues",
        ),
        # ('<i class="fa fa-envelope fa-fw"></i> Mailing List', 'https://groups.io/g/scherbelberg-dev'),
        # ('<i class="fa fa-comments fa-fw"></i> Chat', 'https://matrix.to/#/#scherbelberg:matrix.org'),
        # ('<i class="fa fa-file-text fa-fw"></i> Citation', 'https://doi.org/000'),
        (
            '<i class="fa fa-info-circle fa-fw"></i> pleiszenburg.de',
            "http://www.pleiszenburg.de/",
        ),
    ],
}

always_document_param_types = True  # sphinx_autodoc_typehints

napoleon_include_special_with_doc = True  # napoleon
# napoleon_use_param = True
# napoleon_type_aliases = True
