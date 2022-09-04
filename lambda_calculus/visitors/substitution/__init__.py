#!/usr/bin/python3

"""Visitors for variable substitution"""

from __future__ import annotations
from abc import abstractmethod
from typing import TypeVar, Type, final
from .. import Visitor, DeferrableVisitor
from ... import terms

__all__ = (
    "Substitution",
    "DeferrableSubstitution",
    "checked",
    "unsafe"
)

T = TypeVar("T")
V = TypeVar("V")


class Substitution(Visitor["terms.Term[V]", V]):
    """ABC for Visitors which replace a free Variable with another term"""

    __slots__ = ()

    @abstractmethod
    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> terms.Abstraction[V]:
        """visit an Abstraction term"""
        raise NotImplementedError()

    @abstractmethod
    def visit_application(self, application: terms.Application[V]) -> terms.Application[V]:
        """visit an Application term"""
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_substitution(cls: Type[T], variable: V, value: terms.Term[V]) -> T:
        """create an instance from the substitution it should perform"""
        raise NotImplementedError()


class DeferrableSubstitution(DeferrableVisitor["terms.Term[V]", V], Substitution[V]):
    """ABC for Substitutions which can be performed lazyly"""

    __slots__ = ()

    @abstractmethod
    def defer_abstraction(self, abstraction: terms.Abstraction[V]) -> tuple[terms.Abstraction[V], DeferrableSubstitution[V] | None]:
        """visit an Abstraction term and return the visitor used to visit its body"""
        raise NotImplementedError()

    @abstractmethod
    def defer_application(self, application: terms.Application[V]) -> tuple[terms.Application[V], DeferrableSubstitution[V] | None, DeferrableSubstitution[V] | None]:
        """visit an Application term and return the visitors used to visit its abstraction and argument"""
        raise NotImplementedError()

    @final
    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> terms.Abstraction[V]:
        """visit an Abstraction term"""
        substituted, body_visitor = self.defer_abstraction(abstraction)
        if body_visitor is None:
            return substituted
        return terms.Abstraction(
            substituted.bound,
            substituted.body.accept(body_visitor)
        )

    @final
    def visit_application(self, application: terms.Application[V]) -> terms.Application[V]:
        """visit an Application term"""
        substituted, abstraction_visitor, argument_visitor = self.defer_application(application)
        if abstraction_visitor is None:
            abstraction = substituted.abstraction
        else:
            abstraction = substituted.abstraction.accept(abstraction_visitor)
        if argument_visitor is None:
            argument = substituted.argument
        else:
            argument = substituted.argument.accept(argument_visitor)
        return terms.Application(abstraction, argument)
