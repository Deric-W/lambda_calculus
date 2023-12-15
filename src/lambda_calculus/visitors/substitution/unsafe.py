#!/usr/bin/python3

"""Substitutions which dont check if the substitutions are valid"""

from __future__ import annotations
from typing import TypeVar, final
from ... import terms
from . import DeferrableSubstitution

__all__ = (
    "UnsafeSubstitution",
)

V = TypeVar("V")


@final
class UnsafeSubstitution(DeferrableSubstitution[V]):
    """
    Substitution which does not check if a free variable gets bound.

    :param variable: variable to substitute
    :param value: value which should be substituted
    """

    variable: V

    value: terms.Term[V]

    __slots__ = (
        "variable",
        "value"
    )

    def __init__(self, variable: V, value: terms.Term[V]) -> None:
        self.variable = variable
        self.value = value

    @classmethod
    def from_substitution(cls, variable: V, value: terms.Term[V]) -> UnsafeSubstitution[V]:
        """
        Create an instance from the substitution it should perform

        :param variable: variable to substitute
        :param value: value which should be substituted
        :return: new instance
        """
        return cls(variable, value)

    def visit_variable(self, variable: terms.Variable[V]) -> terms.Term[V]:
        """
        Visit a Variable term.

        :param variable: variable term to visit
        :return: variable term or value which should be substituted
        """
        if variable.name != self.variable:
            return variable
        return self.value

    def defer_abstraction(self, abstraction: terms.Abstraction[V]) -> tuple[terms.Abstraction[V], UnsafeSubstitution[V] | None]:
        """
        Visit an Abstraction term.

        :param abstraction: abstraction term to visit
        :return: tuple containing the abstraction term and this visitor
                 to be used for visiting its body if variable is not bound
        """
        if abstraction.bound == self.variable:
            return abstraction, None
        return abstraction, self

    def defer_application(self, application: terms.Application[V]) -> tuple[terms.Application[V], UnsafeSubstitution[V], UnsafeSubstitution[V]]:
        """
        Visit an Application term.

        :param application: application term to visit
        :return: tuple containing the application term and this visitor
                 to be used for visiting its abstraction and argument
        """
        return application, self, self
