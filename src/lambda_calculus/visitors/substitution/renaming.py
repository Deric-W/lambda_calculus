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
    ABC for Substitutions which rename
    bound variables if a free variable gets bound.
    """

    variable: V

    value: terms.Term[V]

    __slots__ = (
        "variable",
        "value"
    )

    @abstractmethod
    def prevent_collision(self, abstraction: terms.Abstraction[V]) -> terms.Abstraction[V]:
        """
        Prevent collisions by renaming bound variables.

        :param abstraction: abstraction term which could bind free variables
        :return: abstraction term which does not bind free variables
        """
        raise NotImplementedError()

    @final
    def trace(self) -> TracingDecorator[V]:
        """
        Create a new visitor which yields when an alpha conversion occurs.

        :return: new visitor wrapping this instance
        """
        return TracingDecorator(self)

    @final
    def visit_variable(self, variable: terms.Variable[V]) -> terms.Term[V]:
        """
        Visit a Variable term.

        :param variable: variable term to visit
        :return: variable term or value which should be substituted
        """
        if variable.name != self.variable:
            return variable
        return self.value

    @final
    def defer_abstraction(self, abstraction: terms.Abstraction[V]) -> tuple[terms.Abstraction[V], RenamingSubstitution[V] | None]:
        """
        Visit an Abstraction term.

        :param abstraction: abstraction term to visit
        :return: tuple containing an abstraction term not binding free variables and
                 this visitor to be used for visiting its body if variable is not bound
        """
        if abstraction.bound == self.variable:
            return abstraction, None
        return self.prevent_collision(abstraction), self

    @final
    def defer_application(self, application: terms.Application[V]) -> tuple[terms.Application[V], RenamingSubstitution[V], RenamingSubstitution[V]]:
        """
        Visit an Application term.

        :param application: application term to visit
        :return: tuple containing the application term and this visitor
                 to be used for visiting its abstraction and argument
        """
        return application, self, self


@final
class TracingDecorator(Visitor[Generator["terms.Term[V]", None, "terms.Term[V]"], V]):
    """
    Visitor which transforms a :class:`RenamingSubstitution` into an Generator
    which yields after performing an alpha conversion and returns the term with substitutions.

    :param substitution: instance to wrap
    """

    substitution: RenamingSubstitution[V]

    __slots__ = ("substitution",)

    def __init__(self, substitution: RenamingSubstitution[V]) -> None:
        self.substitution = substitution

    def visit_variable(self, variable: terms.Variable[V]) -> Generator[terms.Variable[V], None, terms.Term[V]]:
        """
        Visit a Variable term.

        :param variable: variable term to visit
        :return: empty Generator returning the result
                 of :meth:`RenamingSubstitution.visit_variable`
        """
        return self.substitution.visit_variable(variable)
        # to create a generator
        yield variable  # type: ignore[unreachable]

    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> Generator[terms.Abstraction[V], None, terms.Abstraction[V]]:
        """
        Visit an Abstraction term

        :param abstraction: abstraction term to visit
        :return: Generator yielding alpha conversions and
                 returning the term with substitutions
        """
        substituted, visitor = self.substitution.defer_abstraction(abstraction)
        if visitor is None:
            return substituted
        elif substituted.bound != abstraction.bound:
            yield substituted
        conversions = substituted.body.accept(self)
        body = yield from map(lambda b: terms.Abstraction(substituted.bound, b), conversions)
        return terms.Abstraction(substituted.bound, body)

    def visit_application(self, application: terms.Application[V]) -> Generator[terms.Application[V], None, terms.Application[V]]:
        """
        Visit an Application term

        :param appliation: application term to visit
        :return: Generator yielding alpha conversions and
                 returning the term with substitutions
        """
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
    Substitution which renames bound variables
    if a free variable gets bound by appending a number.

    :param variable: variable to substitute
    :param value: value which should be substituted
    :param free_variables: free variables which should not be bound
    """

    free_variables: Set[str]

    __slots__ = ("free_variables",)

    def __init__(self, variable: str, value: terms.Term[str], free_variables: Set[str]) -> None:
        self.variable = variable
        self.value = value
        self.free_variables = free_variables

    @classmethod
    def from_substitution(cls, variable: str, value: terms.Term[str]) -> CountingSubstitution:
        """
        Create an instance from the substitution it should perform

        :param variable: variable to substitute
        :param value: value which should be substituted
        :return: new instance with free_variables set to the free variables of value
        """
        return cls(variable, value, value.free_variables())

    def prevent_collision(self, abstraction: terms.Abstraction[str]) -> terms.Abstraction[str]:
        """
        Prevent collisions by appending a number.

        :param abstraction: abstraction term which could bind free variables
        :return: abstraction term which does not bind free variables
        """
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
