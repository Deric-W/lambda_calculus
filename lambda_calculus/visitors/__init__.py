#!/usr/bin/python3

"""Visitors for performing operations on Terms"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, final
from .. import terms

__all__ = (
    "Visitor",
    "BottomUpVisitor",
    "DeferrableVisitor",
    "substitution",
    "normalisation",
    "walking"
)

T = TypeVar("T")
V = TypeVar("V")


class Visitor(ABC, Generic[T, V]):
    """
    ABC for Visitors visiting Terms
    The visitor is responsible to visit child terms
    """

    __slots__ = ()

    @final
    def visit(self, term: terms.Term[V]) -> T:
        """visit a term"""
        return term.accept(self)

    @abstractmethod
    def visit_variable(self, variable: terms.Variable[V]) -> T:
        """visit a Variable term"""
        raise NotImplementedError()

    @abstractmethod
    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> T:
        """visit an Abstraction term"""
        raise NotImplementedError()

    @abstractmethod
    def visit_application(self, application: terms.Application[V]) -> T:
        """visit an Application term"""
        raise NotImplementedError()


class BottomUpVisitor(Visitor[T, V]):
    """ABC for visitors which visit child terms first"""

    __slots__ = ()

    @final
    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> T:
        """visit an Abstraction term"""
        return self.ascend_abstraction(
            abstraction,
            abstraction.body.accept(self)
        )

    @final
    def visit_application(self, application: terms.Application[V]) -> T:
        """visit an Application term"""
        return self.ascend_application(
            application,
            application.abstraction.accept(self),
            application.argument.accept(self)
        )

    @abstractmethod
    def ascend_abstraction(self, abstraction: terms.Abstraction[V], body: T) -> T:
        """visit an Abstraction term after visiting its body"""
        raise NotImplementedError()

    @abstractmethod
    def ascend_application(self, application: terms.Application[V], abstraction: T, argument: T) -> T:
        """visit an Application term after visiting its abstraction and argument"""
        raise NotImplementedError()


class DeferrableVisitor(Visitor[T, V]):
    """ABC for visitors which can visit terms top down lazyly"""

    __slots__ = ()

    @abstractmethod
    def defer_abstraction(self, abstraction: terms.Abstraction[V]) -> tuple[T, DeferrableVisitor[T, V] | None]:
        """visit an Abstraction term and return the visitor used to visit its body"""
        raise NotImplementedError()

    @abstractmethod
    def defer_application(self, application: terms.Application[V]) -> tuple[T, DeferrableVisitor[T, V] | None, DeferrableVisitor[T, V] | None]:
        """visit an Application term and return the visitors used to visit its abstraction and argument"""
        raise NotImplementedError()
