#!/usr/bin/python3

"""Substitutions which dont check if the substitutions are valid"""

from __future__ import annotations
from collections.abc import Set
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
    Visitor which replaces a free Variable with another term
    Does nothing if a free variable gets bound
    """

    variable: V

    value: terms.Term[V]

    free_variables: Set[V]

    __slots__ = (
        "variable",
        "value",
        "free_variables"
    )

    def __init__(self, variable: V, value: terms.Term[V], free_variables: Set[V]) -> None:
        self.variable = variable
        self.value = value
        self.free_variables = free_variables

    @classmethod
    def from_substitution(cls, variable: V, value: terms.Term[V]) -> UnsafeSubstitution[V]:
        """create an instance from the substitution it should perform"""
        return cls(variable, value, value.free_variables())

    def visit_variable(self, variable: terms.Variable[V]) -> terms.Term[V]:
        """visit a Variable term"""
        if variable.name != self.variable:
            return variable
        return self.value

    def defer_abstraction(self, abstraction: terms.Abstraction[V]) -> tuple[terms.Abstraction[V], UnsafeSubstitution[V] | None]:
        """visit an Abstraction term and return the visitor used to visit its body"""
        if abstraction.bound == self.variable:
            return abstraction, None
        return abstraction, self

    def defer_application(self, application: terms.Application[V]) -> tuple[terms.Application[V], UnsafeSubstitution[V], UnsafeSubstitution[V]]:
        """visit an Application term and return the visitors used to visit its abstraction and argument"""
        return application, self, self
