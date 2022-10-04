#!/usr/bin/python3

"""Implementations of boolean values and logical operators"""

from typing import Final
from . import Variable, Abstraction, Application

__all__ = (
    "TRUE",
    "FALSE",
    "AND",
    "OR",
    "NOT",
    "IF_THEN_ELSE"
)

TRUE: Final = Abstraction.curried(("x", "y"), Variable("x"))
"""
Term representing True.
"""

FALSE: Final = Abstraction.curried(("x", "y"), Variable("y"))
"""
Term representing False
"""

AND: Final = Abstraction.curried(
    ("p", "q"),
    Application.with_arguments(Variable("p"), (Variable("q"), Variable("p")))
)
"""
Term implementing logical conjunction between its two arguments.
"""

OR: Final = Abstraction.curried(
    ("p", "q"),
    Application.with_arguments(Variable("p"), (Variable("p"), Variable("q")))
)
"""
Term implementing logical disjunction between its two arguments.
"""

NOT: Final = Abstraction("p", Application.with_arguments(Variable("p"), (FALSE, TRUE)))
"""
Term performing logical negation of its argument.
"""

IF_THEN_ELSE: Final = Abstraction.curried(
    ("p", "a", "b"),
    Application.with_arguments(Variable("p"), (Variable("a"), Variable("b")))
)
"""
Term evaluating to its second argument if its first argument is TRUE
or its third argument otherwise.
"""
