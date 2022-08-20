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
    """Visitor yielding subterms depth first"""

    def visit_variable(self, variable: terms.Variable[V]) -> Iterator[terms.Term[V]]:
        """visit a Variable term"""
        yield variable

    def ascend_abstraction(
        self,
        abstraction: terms.Abstraction[V],
        body: Iterator[terms.Term[V]]
    ) -> Iterator[terms.Term[V]]:
        """visit an Abstraction term after visiting its body"""
        yield from body
        yield abstraction

    def ascend_application(
        self,
        application: terms.Application[V],
        abstraction: Iterator[terms.Term[V]],
        argument: Iterator[terms.Term[V]]
    ) -> Iterator[terms.Term[V]]:
        """visit an Application term after visiting its abstraction and argument"""
        yield from abstraction
        yield from argument
        yield application
