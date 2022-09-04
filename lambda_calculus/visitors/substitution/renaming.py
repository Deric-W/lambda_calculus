#!/usr/bin/python3

"""Substitutions performing automatic alpha conversion"""

from __future__ import annotations
from abc import abstractmethod
from collections.abc import Set, Generator
from itertools import count, filterfalse
from typing import TypeVar, final
from . import DeferrableSubstitution
from .unsafe import UnsafeSubstitution
from .. import Visitor
from ... import terms

__all__ = (
    "RenamingSubstitution",
    "TracingDecorator",
    "CountingSubstitution"
)

V = TypeVar("V")


class RenamingSubstitution(DeferrableSubstitution[V]):
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

    @final
    def trace(self) -> TracingDecorator[V]:
        """return a new visitor which yields when an alpha conversion occurs"""
        return TracingDecorator(self)

    @final
    def visit_variable(self, variable: terms.Variable[V]) -> terms.Term[V]:
        """visit a Variable term"""
        if variable.name != self.variable:
            return variable
        return self.value

    @final
    def defer_abstraction(self, abstraction: terms.Abstraction[V]) -> tuple[terms.Abstraction[V], RenamingSubstitution[V] | None]:
        """visit an Abstraction term and return the visitor used to visit its body"""
        if abstraction.bound == self.variable:
            return abstraction, None
        return self.prevent_collision(abstraction), self

    @final
    def defer_application(self, application: terms.Application[V]) -> tuple[terms.Application[V], RenamingSubstitution[V], RenamingSubstitution[V]]:
        """visit an Application term and return the visitors used to visit its abstraction and argument"""
        return application, self, self


@final
class TracingDecorator(Visitor[Generator["terms.Term[V]", None, "terms.Term[V]"], V]):
    """
    Visitor which transforms a RenamingSubstitution into an Generator
    which yields after performing an alpha conversion
    """

    substitution: RenamingSubstitution[V]

    __slots__ = ("substitution",)

    def __init__(self, substitution: RenamingSubstitution[V]) -> None:
        self.substitution = substitution

    def visit_variable(self, variable: terms.Variable[V]) -> Generator[terms.Variable[V], None, terms.Term[V]]:
        """visit a Variable term"""
        return self.substitution.visit_variable(variable)
        # to create a generator
        yield variable  # type: ignore[unreachable]

    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> Generator[terms.Abstraction[V], None, terms.Abstraction[V]]:
        """visit an Abstraction term"""
        substituted, visitor = self.substitution.defer_abstraction(abstraction)
        if visitor is None:
            return substituted
        elif substituted.bound != abstraction.bound:
            yield substituted
        conversions = substituted.body.accept(self)
        body = yield from map(lambda b: terms.Abstraction(substituted.bound, b), conversions)
        return terms.Abstraction(substituted.bound, body)

    def visit_application(self, application: terms.Application[V]) -> Generator[terms.Application[V], None, terms.Application[V]]:
        """visit an Application term"""
        # distinguish between last alpha conversion (step) and
        # substituted abstraction (abstraction)
        abstraction = step = application.abstraction
        conversions = application.abstraction.accept(self)
        while True:
            try:
                step = next(conversions)
            except StopIteration as stop:
                abstraction = stop.value
                break
            else:
                yield terms.Application(step, application.argument)
        conversions = application.argument.accept(self)
        argument = yield from map(lambda a: terms.Application(step, a), conversions)
        return terms.Application(abstraction, argument)


@final
class CountingSubstitution(RenamingSubstitution[str]):
    """
    Visitor which replaces a free Variable with another term
    Renames bound variables if a free variable gets bound by appending a number
    """

    free_variables: Set[str]

    __slots__ = ("free_variables",)

    def __init__(self, variable: str, value: terms.Term[str], free_variables: Set[str]) -> None:
        self.variable = variable
        self.value = value
        self.free_variables = free_variables

    @classmethod
    def from_substitution(cls, variable: str, value: terms.Term[str]) -> CountingSubstitution:
        """create an instance from the substitution it should perform"""
        return cls(variable, value, value.free_variables())

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
                abstraction.body.accept(
                    UnsafeSubstitution.from_substitution(
                        abstraction.bound,
                        terms.Variable(variable)
                    )
                )
            )
        else:
            return abstraction
