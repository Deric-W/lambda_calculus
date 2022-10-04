#!/usr/bin/python3

"""Visitor for walking terms"""

from __future__ import annotations
from collections.abc import Iterator
from typing import TypeVar
from .. import terms
from . import BottomUpVisitor

__all__ = (
    "DepthFirstVisitor",
)

V = TypeVar("V")


class DepthFirstVisitor(BottomUpVisitor[Iterator["terms.Term[V]"], V]):
    """
    Visitor yielding subterms depth first

    Type Variables:

        V: represents the type of variables used in terms
    """

    def visit_variable(self, variable: terms.Variable[V]) -> Iterator[terms.Term[V]]:
        """
        Visit a Variable term.

        :param variable: variable term to visit
        :return: Iterator yielding the term
        """
        yield variable

    def ascend_abstraction(
        self,
        abstraction: terms.Abstraction[V],
        body: Iterator[terms.Term[V]]
    ) -> Iterator[terms.Term[V]]:
        """
        Visit an Abstraction term after visiting its body.

        :param abstraction: abstraction term to visit
        :param body: Iterator produced by visiting its body
        :return: term appended to its body Iterator
        """
        yield from body
        yield abstraction

    def ascend_application(
        self,
        application: terms.Application[V],
        abstraction: Iterator[terms.Term[V]],
        argument: Iterator[terms.Term[V]]
    ) -> Iterator[terms.Term[V]]:
        """
        Visit an Application term after visiting its abstraction and argument.

        :param application: application term to visit
        :param abstraction: Iterator produced by visiting its abstraction
        :param argument: Iterator produced by visiting its argument
        :return: term appended to its abstraction and argument Iterators
        """
        yield from abstraction
        yield from argument
        yield application
