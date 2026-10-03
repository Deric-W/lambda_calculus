"""Implementations of natural numbers and arithmetic operators"""

from typing import Final

from . import Abstraction, Application, Term, Variable
from .logic import FALSE, TRUE

__all__ = ("ADD", "ISZERO", "MULTIPLY", "POWER", "PREDECESSOR", "SUBTRACT", "SUCCESSOR", "number")

ISZERO: Final = Variable("n").apply_to(FALSE.abstract("x"), TRUE).abstract("n")
"""
Term which evaluates to :const:`lambda_calculus.terms.logic.TRUE`
if its argument is zero, :const:`lambda_calculus.terms.logic.FALSE` otherwise
"""

SUCCESSOR: Final = Abstraction.curried(
    ("n", "f", "x"),
    Application(
        Variable("f"), Application.with_arguments(Variable("n"), (Variable("f"), Variable("x")))
    ),
)
"""
Term evaluating to its argument incremented by one.
"""

PREDECESSOR: Final = Abstraction.curried(
    ("n", "f", "x"),
    Application.with_arguments(
        Variable("n"),
        (
            Abstraction.curried(
                ("g", "h"), Application(Variable("h"), Application(Variable("g"), Variable("f")))
            ),
            Abstraction("u", Variable("x")),
            Abstraction("u", Variable("u")),
        ),
    ),
)
"""
Term ealuating to its argument decremented by one.
"""

ADD: Final = Abstraction.curried(
    ("m", "n", "f", "x"),
    Application.with_arguments(
        Variable("m"),
        (Variable("f"), Application.with_arguments(Variable("n"), (Variable("f"), Variable("x")))),
    ),
)
"""
Term evaluating to the sum of its two arguments.
"""

SUBTRACT: Final = Abstraction.curried(
    ("m", "n"), Application.with_arguments(Variable("n"), (PREDECESSOR, Variable("m")))
)
"""
Term evaluating to the difference of its two arguments.
"""

MULTIPLY: Final = Abstraction.curried(
    ("m", "n", "f"), Application(Variable("m"), Application(Variable("n"), Variable("f")))
)
"""
Term evaluating to the product of its two arguments.
"""

POWER: Final = Abstraction.curried(("b", "e"), Application(Variable("e"), Variable("b")))
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
        msg = "number is not natural"
        raise ValueError(msg)
    f = Variable("f")
    body: Term[str] = Variable("x")
    for _ in range(n):
        body = Application(f, body)
    return Abstraction.curried(("f", "x"), body)
