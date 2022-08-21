#!/usr/bin/python3

"""Implementations of boolean values and logical operators"""

from . import Variable, Abstraction, Application

__all__ = (
    "TRUE",
    "FALSE",
    "AND",
    "OR",
    "NOT",
    "IF_THEN_ELSE"
)

TRUE = Abstraction.curried(("x", "y"), Variable("x"))
FALSE = Abstraction.curried(("x", "y"), Variable("y"))

AND = Abstraction.curried(
    ("p", "q"),
    Application.with_arguments(Variable("p"), (Variable("q"), Variable("p")))
)
OR = Abstraction.curried(
    ("p", "q"),
    Application.with_arguments(Variable("p"), (Variable("p"), Variable("q")))
)
NOT = Abstraction("p", Application.with_arguments(Variable("p"), (FALSE, TRUE)))

IF_THEN_ELSE = Abstraction.curried(
    ("p", "a", "b"),
    Application.with_arguments(Variable("p"), (Variable("a"), Variable("b")))
)
