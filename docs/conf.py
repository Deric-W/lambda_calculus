"""Sphinx configuration"""

import os.path
import sys

from sphinx_pyproject import SphinxConfig

from lambda_calculus import __version__ as version

sys.path.append(os.path.abspath(".."))

config = SphinxConfig(
    "../pyproject.toml", globalns=globals(), config_overrides={"version": version}
)

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/stable/", None),
}
