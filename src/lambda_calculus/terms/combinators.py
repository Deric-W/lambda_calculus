#!/usr/bin/python3

"""Common combinators"""

from typing import Final
from . import Variable, Application

__all__ = (
    "Y",
    "S",
    "K",
    "I",
    "B",
    "C",
    "W",
    "DELTA",
    "OMEGA"
)

Y: Final = Application(
    Variable("g").apply_to(
        Variable("x").apply_to(Variable("x"))
    ).abstract("x"),
    Variable("g").apply_to(
        Variable("x").apply_to(Variable("x"))
    ).abstract("x")
).abstract("g")
"""
Y combinator used to define recursive terms.
"""

S: Final = Variable("x").apply_to(
    Variable("z"),
    Variable("y").apply_to(Variable("z"))
).abstract("x", "y", "z")
"""
S combinator of the SKI combinator calculus.
"""

K: Final = Variable("x").abstract("x", "y")
"""
K combinator of the SKI combinator calculus.
"""

I: Final = Variable("x").abstract("x")
"""
I combinator of the SKI combinator calculus.
"""

B: Final = Variable("x").apply_to(
    Variable("y").apply_to(Variable("z"))
).abstract("x", "y", "z")
"""
B combinator of the BCKW combinator calculus.
"""

C: Final = Variable("x").apply_to(
    Variable("z"),
    Variable("y")
).abstract("x", "y", "z")
"""
C combinator of the BCKW combinator calculus.
"""

W: Final = Variable("x").apply_to(
    Variable("y"),
    Variable("y")
).abstract("x", "y")
"""
W combinator of the BCKW combinator calculus.
"""

DELTA: Final = Variable("x").apply_to(
    Variable("x")
).abstract("x")
"""
Term applying its argument to itself.
"""

OMEGA: Final = DELTA.apply_to(DELTA)
"""
Smallest term with no beta normal form.
"""
