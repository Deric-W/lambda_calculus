"""Implementation of the Lambda calculus"""

from ._version import version as __version__  # noqa: F401
from .terms import Abstraction, Application, Variable

__author__ = "Eric Niklas Wolf"
__email__ = "eric_niklas.wolf@mailbox.tu-dresden.de"
__all__ = ("Abstraction", "Application", "Variable", "errors", "terms", "visitors")
