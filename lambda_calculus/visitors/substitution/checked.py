#!/usr/bin/python3

"""Substitutions checking if the substitutions are valid"""

from __future__ import annotations
from collections.abc import Set
from typing import TypeVar, final
from ... import terms
from ...errors import CollisionError
from . import Substitution

__all__ = (
    "CheckedSubstitution",
)

V = TypeVar("V")


@final
class CheckedSubstitution(Substitution[V]):
    """
    Substitution which checks if a free variable gets bound.

    :param variable: variable to substitute
    :param value: value which should be substituted
    :param free_variables: free variables which should not be bound
    :raise errors.CollisionError: If a free variable gets bound
    """

    variable: V

    value: terms.Term[V]

    free_variables: Set[V]

    bound_variables: dict[V, int]

    __slots__ = (
        "variable",
        "value",
        "free_variables",
        "bound_variables"
    )

    def __init__(self, variable: V, value: terms.Term[V], free_variables: Set[V]) -> None:
        self.variable = variable
        self.value = value
        self.free_variables = free_variables
        # store number of binds since a variable can be bound multiple times
        self.bound_variables = {}

    @classmethod
    def from_substitution(cls, variable: V, value: terms.Term[V]) -> CheckedSubstitution[V]:
        """
        Create an instance from the substitution it should perform

        :param variable: variable to substitute
        :param value: value which should be substituted
        :return: new instance with free_variables set to the free variables of value
        """
        return cls(variable, value, value.free_variables())

    def bind_variable(self, name: V) -> None:
        """
        Mark a variable as bound.

        Bound variables are not automatically unbound
        and can be bound multiple times.

        :param name: name of the variable
        """
        self.bound_variables[name] = self.bound_variables.get(name, 0) + 1

    def unbind_variable(self, name: V) -> None:
        """
        Mark a variable as not bound.

        A variable needs to be unbound multiple times
        if it was bound multiple times.

        :param name: name of the variable
        :raise KeyError: If the variable is not bound
        """
        number = self.bound_variables[name]
        if number == 1:
            del self.bound_variables[name]
        else:
            self.bound_variables[name] = number - 1

    def visit_variable(self, variable: terms.Variable[V]) -> terms.Term[V]:
        """
        Visit a Variable term.

        :param variable: variable term to visit
        :raise errors.CollisionError: If the substitution whould bind free variables
        :return: variable term or value which should be substituted
        """
        if variable.name != self.variable:
            return variable
        collisions = self.free_variables & self.bound_variables.keys()
        if collisions:
            raise CollisionError("free variables in value are bound in term", collisions)
        return self.value

    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> terms.Abstraction[V]:
        """
        Visit an Abstraction term.

        :param abstraction: abstraction term to visit
        :raise errors.CollisionError: If a substitution in the body
                                      whould bind free variables
        :return: abstraction term or new term with substitutions performed
        """
        if abstraction.bound == self.variable:
            return abstraction
        self.bind_variable(abstraction.bound)
        try:
            return terms.Abstraction(
                abstraction.bound,
                abstraction.body.accept(self)
            )
        finally:
            # allow reuse of this visitor, even on error
            self.unbind_variable(abstraction.bound)

    def visit_application(self, application: terms.Application[V]) -> terms.Application[V]:
        """
        Visit an Application term.

        :param appliation: application term to visit
        :raise errors.CollisionError: If a substitution in the abstraction
                                      or argument whould bind free variables
        :return: new term with substitutions performed
        """
        return terms.Application(
            application.abstraction.accept(self),
            application.argument.accept(self)
        )
