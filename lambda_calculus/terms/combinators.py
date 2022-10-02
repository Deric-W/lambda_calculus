#!/usr/bin/python3

"""Common combinators"""

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

Y = Application(
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

S = Variable("x").apply_to(
    Variable("z"),
    Variable("y").apply_to(Variable("z"))
).abstract("x", "y", "z")
"""
S combinator of the SKI combinator calculus.
"""

K = Variable("x").abstract("x", "y")
"""
K combinator of the SKI combinator calculus.
"""

I = Variable("x").abstract("x")
"""
I combinator of the SKI combinator calculus.
"""

B = Variable("x").apply_to(
    Variable("y").apply_to(Variable("z"))
).abstract("x", "y", "z")
"""
B combinator of the BCKW combinator calculus.
"""

C = Variable("x").apply_to(
    Variable("z"),
    Variable("y")
).abstract("x", "y", "z")
"""
C combinator of the BCKW combinator calculus.
"""

W = Variable("x").apply_to(
    Variable("y"),
    Variable("y")
).abstract("x", "y")
"""
W combinator of the BCKW combinator calculus.
"""

DELTA = Variable("x").apply_to(
    Variable("x")
).abstract("x")
"""
Term applying its argument to itself.
"""

OMEGA = DELTA.apply_to(DELTA)
"""
Smallest term with no beta normal form.
"""
