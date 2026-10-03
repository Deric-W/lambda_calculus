"""Implementation of pairs"""

from typing import Final

from . import Abstraction, Application, Variable
from .logic import FALSE, TRUE

__all__ = ("FIRST", "NIL", "NULL", "PAIR", "SECOND")

PAIR: Final = Abstraction.curried(
    ("x", "y", "f"), Application.with_arguments(Variable("f"), (Variable("x"), Variable("y")))
)
"""
Term evaluating to a ordered pair of its two arguments.
"""

FIRST: Final = Abstraction("p", Application(Variable("p"), TRUE))
"""
Term evaluating to the first value in its argument.
"""

SECOND: Final = Abstraction("p", Application(Variable("p"), FALSE))
"""
Term evaluating to the second value in its argument.
"""

NIL: Final = Abstraction("x", TRUE)
"""
Special Term encoding an empty pair.
"""

NULL: Final = Abstraction("p", Application(Variable("p"), Abstraction.curried(("x", "y"), FALSE)))
"""
Term evaluating to logic.TRUE if its argument is NIL, logic.FALSE otherwise.
"""
