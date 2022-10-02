#!/usr/bin/python3

"""Implementations of natural numbers and arithmetic operators"""

from . import Term, Variable, Abstraction, Application
from .logic import TRUE, FALSE

__all__ = (
    "ISZERO",
    "SUCCESSOR",
    "PREDECESSOR",
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "POWER",
    "number"
)

ISZERO = Variable("n").apply_to(FALSE.abstract("x"), TRUE).abstract("n")
"""
Term which evaluates to logic.TRUE if its argument is zero, logic.FALSE otherwise
"""

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
"""
Term evaluating to its argument incremented by one.
"""

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
"""
Term ealuating to its argument decremented by one.
"""

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
"""
Term evaluating to the sum of its two arguments.
"""

SUBTRACT = Abstraction.curried(
    ("m", "n"),
    Application.with_arguments(
        Variable("n"),
        (PREDECESSOR, Variable("m"))
    )
)
"""
Term evaluating to the difference of its two arguments.
"""

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
"""
Term evaluating to the product of its two arguments.
"""

POWER = Abstraction.curried(
    ("b", "e"),
    Application(
        Variable("e"),
        Variable("b")
    )
)
"""
Term evaluating to its first argument to the power of its second argument.
"""


def number(n: int) -> Abstraction[str]:
    """
    Encode a number as a lambda term.

    :param n: number to encode
    :raise ValueError: If the number is negative
    :return: requested term
    """
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
