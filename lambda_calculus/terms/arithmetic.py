#!/usr/bin/python3

"""Implementations of natural numbers and arithmetic operators"""

from . import Term, Variable, Abstraction, Application

__all__ = (
    "SUCCESSOR",
    "PREDECESSOR",
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "POWER",
    "number"
)

SUCCESSOR = Abstraction.curried(
    ("n", "f", "x"),
    Application(
        Variable("f"),
        Application.with_arguments(
            Variable("n"),
            (Variable("f"), Variable("x"))
        )
    )
)

PREDECESSOR = Abstraction.curried(
    ("n", "f", "x"),
    Application.with_arguments(
        Variable("n"),
        (
            Abstraction.curried(
                ("g", "h"),
                Application(
                    Variable("h"),
                    Application(
                        Variable("g"),
                        Variable("f")
                    )
                )
            ),
            Abstraction("u", Variable("x")),
            Abstraction("u", Variable("u")),
        )
    )
)

ADD = Abstraction.curried(
    ("m", "n", "f", "x"),
    Application.with_arguments(
        Variable("m"),
        (
            Variable("f"),
            Application.with_arguments(
                Variable("n"),
                (Variable("f"), Variable("x"))
            )
        )
    )
)

SUBTRACT = Abstraction.curried(
    ("m", "n"),
    Application.with_arguments(
        Variable("n"),
        (PREDECESSOR, Variable("m"))
    )
)

MULTIPLY = Abstraction.curried(
    ("m", "n", "f"),
    Application(
        Variable("m"),
        Application(
            Variable("n"),
            Variable("f")
        )
    )
)

POWER = Abstraction.curried(
    ("b", "e"),
    Application(
        Variable("e"),
        Variable("b")
    )
)


def number(n: int) -> Abstraction[str]:
    """return n encoded in lambda terms"""
    if n < 0:
        raise ValueError("number is not natural")
    f = Variable("f")
    body: Term[str] = Variable("x")
    for _ in range(n):
        body = Application(f, body)
    return Abstraction.curried(
        ("f", "x"),
        body
    )
