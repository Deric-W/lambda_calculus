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
    ABC for Visitors visiting Terms.

    The visitor is responsible for visiting child terms.

    Type Variables:

        T: represents the type of the result produced by visiting terms
        V: represents the type of variables used in terms
    """

    __slots__ = ()

    @final
    def visit(self, term: terms.Term[V]) -> T:
        """
        Visit a term

        :param  term: term to visit
        :return: Result of calling :meth:`.terms.Term.accept` with self as argument
        """
        return term.accept(self)

    @abstractmethod
    def visit_variable(self, variable: terms.Variable[V]) -> T:
        """
        Visit a Variable term.

        :param variable: variable term to visit
        :return: value as required by its type variable
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> T:
        """
        Visit an Abstraction term

        The body is not automatically visited.

        :param abstraction: abstraction term to visit
        :return: value as required by its type variable
        """
        raise NotImplementedError()

    @abstractmethod
    def visit_application(self, application: terms.Application[V]) -> T:
        """
        Visit an Application term

        The abstraction and argument are not automatically visited.

        :param appliation: application term to visit
        :return: value as required by its type variable
        """
        raise NotImplementedError()


class BottomUpVisitor(Visitor[T, V]):
    """
    ABC for visitors which visit child terms first

    Child terms are automatically visited.
    """

    __slots__ = ()

    @final
    def visit_abstraction(self, abstraction: terms.Abstraction[V]) -> T:
        """
        Visit an Abstraction term

        The body is visited before calling :meth:`ascend_abstraction`.

        :param abstraction: abstraction term to visit
        :return: value returned by :meth:`ascend_abstraction`
        """
        return self.ascend_abstraction(
            abstraction,
            abstraction.body.accept(self)
        )

    @final
    def visit_application(self, application: terms.Application[V]) -> T:
        """
        Visit an Application term

        The abstraction and argument are visited
        before calling :meth:`ascend_application`.

        :param application: application term to visit
        :return: value returned by :meth:`ascend_application`
        """
        return self.ascend_application(
            application,
            application.abstraction.accept(self),
            application.argument.accept(self)
        )

    @abstractmethod
    def ascend_abstraction(self, abstraction: terms.Abstraction[V], body: T) -> T:
        """
        Visit an Abstraction term after visiting its body.

        :param abstraction: abstraction term to visit
        :param body: value produced by visiting its body
        :return: value as required by its type variable
        """
        raise NotImplementedError()

    @abstractmethod
    def ascend_application(self, application: terms.Application[V], abstraction: T, argument: T) -> T:
        """
        Visit an Application term after visiting its abstraction and argument.

        :param application: application term to visit
        :param abstraction: value produced by visiting its abstraction
        :param argument: value produced by visiting its argument
        :return: value as required by its type variable
        """
        raise NotImplementedError()


class DeferrableVisitor(Visitor[T, V]):
    """
    ABC for visitors which can visit terms top down lazyly.
    """

    __slots__ = ()

    @abstractmethod
    def defer_abstraction(self, abstraction: terms.Abstraction[V]) -> tuple[T, DeferrableVisitor[T, V] | None]:
        """
        Visit an Abstraction term.

        :param abstraction: abstraction term to visit
        :return: tuple containing a value as required by its type variable
                 and a visitor to be used for visiting its body
        """
        raise NotImplementedError()

    @abstractmethod
    def defer_application(self, application: terms.Application[V]) -> tuple[T, DeferrableVisitor[T, V] | None, DeferrableVisitor[T, V] | None]:
        """
        Visit an Application term.

        :param abstraction: application term to visit
        :return: tuple containing a value as required by its type variable
                 and visitors to be used for visiting its abstraction and argument
        """
        raise NotImplementedError()
