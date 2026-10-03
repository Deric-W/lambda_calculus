"""Sphinx configuration"""

import os.path
import sys

from sphinx_pyproject import SphinxConfig

sys.path.append(os.path.abspath(".."))

config = SphinxConfig("../pyproject.toml", globalns=globals())

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/stable/", None),
}
