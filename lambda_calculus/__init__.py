#!/usr/bin/python3

"""Implementation of the Lambda calculus"""

from .terms import Variable, Abstraction, Application

__version__ = "2.2.3"
__author__  = "Eric Niklas Wolf"
__email__   = "eric_niklas.wolf@mailbox.tu-dresden.de"
__all__ = (
    "Variable",
    "Abstraction",
    "Application",
    "terms",
    "visitors",
    "errors"
)
