"""Implementation of the Lambda calculus"""

from .terms import Abstraction, Application, Variable

__version__ = "3.1.0"
__author__ = "Eric Niklas Wolf"
__email__ = "eric_niklas.wolf@mailbox.tu-dresden.de"
__all__ = ("Abstraction", "Application", "Variable", "errors", "terms", "visitors")
