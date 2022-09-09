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

S = Variable("x").apply_to(
    Variable("z"),
    Variable("y").apply_to(Variable("z"))
).abstract("x", "y", "z")

K = Variable("x").abstract("x", "y")

I = Variable("x").abstract("x")

B = Variable("x").apply_to(
    Variable("y").apply_to(Variable("z"))
).abstract("x", "y", "z")

C = Variable("x").apply_to(
    Variable("z"),
    Variable("y")
).abstract("x", "y", "z")

W = Variable("x").apply_to(
    Variable("y"),
    Variable("y")
).abstract("x", "y")

DELTA = Variable("x").apply_to(
    Variable("x")
).abstract("x")

OMEGA = DELTA.apply_to(DELTA)
