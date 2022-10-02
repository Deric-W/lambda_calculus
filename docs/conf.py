#!/usr/bin/env python3

"""Sphinx configuration"""

import sys
import os.path
from sphinx_pyproject import SphinxConfig


sys.path.append(os.path.abspath(".."))

config = SphinxConfig("../pyproject.toml", globalns=globals())

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/stable/", None),
}
