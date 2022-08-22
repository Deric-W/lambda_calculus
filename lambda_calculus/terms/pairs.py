#!/usr/bin/python3

"""Implementation of pairs"""

from . import Variable, Abstraction, Application
from .logic import TRUE, FALSE

__all__ = (
    "PAIR",
    "FIRST",
    "SECOND",
    "NIL",
    "NULL"
)

PAIR = Abstraction.curried(
    ("x", "y", "f"),
    Application.with_arguments(
        Variable("f"),
        (Variable("x"), Variable("y"))
    )
)

FIRST = Abstraction("p", Application(Variable("p"), TRUE))

SECOND = Abstraction("p", Application(Variable("p"), FALSE))

NIL = Abstraction("x", TRUE)

NULL = Abstraction(
    "p",
    Application(
        Variable("p"),
        Abstraction.curried(
            ("x", "y"),
            FALSE
        )
    )
)
