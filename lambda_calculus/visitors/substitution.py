#!/usr/bin/python3

"""Visitor for substitution"""

from __future__ import annotations
from abc import abstractmethod
from collections.abc import Set
from itertools import count, filterfalse
from typing import TypeVar
from .. import terms
from ..errors import CollisionError
from . import Visitor

__all__ = (
    "SubstitutingVisitor",
    "RenamingSubstitutingVisitor",
    "CountingSubstitutingVisitor"
)

V = TypeVar("V")


class SubstitutingVisitor(Visitor["terms.Term[V]", V]):
    """
    Visitor which replaces a free Variable with another term
    Raises a CollisionError if a free variable gets bound
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

    def __init__(self, variable: V, value: terms.Term[V]) -> None:
        self.variable = variable
        self.value = value
        self.free_variables = value.free_variables()
        # store number of binds since a variable can be bound multiple times
        self.bound_variables = {}

    def bind_variable(self, name: V) -> None:
        """mark a variable as bound"""
        self.bound_variables[name] = self.bound_variables.get(name, 0) + 1

    def unbind_variable(self, name: V) -> None:
        """mark a variable as not bound"""
        number = self.bound_variables[name]
        if number == 1:
            del self.bound_variables[name]
        else:
            self.bound_variables[name] = number - 1

    def visit_variable(self, variable: terms.Variable[V]) -> terms.Term[V]:
        """visit a Variable term"""
        if variable.name != self.variable:
            return variable
        collisions = self.free_variables & self.bound_variables.keys()
        if collisions:
            raise CollisionError("free variables in value are bound in term", collisions)
        return self.value

    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> terms.Abstraction[V]:
        """visit an Abstraction term"""
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
        """visit an Application term"""
        return terms.Application(
            application.abstraction.accept(self),
            application.argument.accept(self)
        )


class RenamingSubstitutingVisitor(Visitor["terms.Term[V]", V]):
    """
    Visitor which replaces a free Variable with another term
    Renames bound variables if a free variable gets bound
    """

    variable: V

    value: terms.Term[V]

    __slots__ = (
        "variable",
        "value"
    )

    @abstractmethod
    def prevent_collision(self, abstraction: terms.Abstraction[V]) -> terms.Abstraction[V]:
        """prevent collisions by renaming bound variables"""
        raise NotImplementedError()

    def visit_variable(self, variable: terms.Variable[V]) -> terms.Term[V]:
        """visit a Variable term"""
        if variable.name != self.variable:
            return variable
        return self.value

    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> terms.Abstraction[V]:
        """visit an Abstraction term"""
        if abstraction.bound == self.variable:
            return abstraction
        renamed = self.prevent_collision(abstraction)
        return terms.Abstraction(
            renamed.bound,
            renamed.body.accept(self)
        )

    def visit_application(self, application: terms.Application[V]) -> terms.Application[V]:
        """visit an Application term"""
        return terms.Application(
            application.abstraction.accept(self),
            application.argument.accept(self)
        )


class CountingSubstitutingVisitor(RenamingSubstitutingVisitor[str]):
    """
    Visitor which replaces a free Variable with another term
    Renames bound variables if a free variable gets bound by appending a number
    """

    free_variables: Set[str]

    __slots__ = ("free_variables",)

    def __init__(self, variable: str, value: terms.Term[str]) -> None:
        self.variable = variable
        self.value = value
        self.free_variables = value.free_variables()

    def prevent_collision(self, abstraction: terms.Abstraction[str]) -> terms.Abstraction[str]:
        """prevent collisions by renaming bound variables"""
        if abstraction.bound in self.free_variables:
            used_variables = abstraction.body.bound_variables() \
                | abstraction.free_variables() \
                | self.free_variables
            candidates = map(lambda i: f"{abstraction.bound}{i}", count(1))
            variable = next(filterfalse(lambda v: v in used_variables, candidates))
            return terms.Abstraction(
                variable,
                abstraction.body.substitute(abstraction.bound, terms.Variable(variable))
            )
        else:
            return abstraction
