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
"""
Term evaluating to a ordered pair of its two arguments.
"""

FIRST = Abstraction("p", Application(Variable("p"), TRUE))
"""
Term evaluating to the first value in its argument.
"""

SECOND = Abstraction("p", Application(Variable("p"), FALSE))
"""
Term evaluating to the second value in its argument.
"""

NIL = Abstraction("x", TRUE)
"""
Special Term encoding an empty pair.
"""

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
"""
Term evaluating to logic.TRUE if its argument is NIL, logic.FALSE otherwise.
"""
