#!/usr/bin/python3

"""Visitor for normalisation"""

from __future__ import annotations
from collections.abc import Iterator
from typing import TypeVar
from .. import terms
from . import Visitor
from .substitution import CountingSubstitutingVisitor

__all__ = (
    "BetaNormalisingVisitor",
)

V = TypeVar("V")


class BetaNormalisingVisitor(Visitor[Iterator[terms.Term[str]], str]):
    """
    Visitor which transforms a term into its beta normal form,
    yielding intermediate results until it is reached
    """

    __slots__ = ()

    def skip_intermediate(self, term: terms.Term[str]) -> terms.Term[str]:
        """return the beta normal form directly"""
        result = term
        for intermediate in term.accept(self):
            result = intermediate
        return result

    def visit_variable(self, variable: terms.Variable[str]) -> Iterator[terms.Variable[str]]:
        """visit a Variable term"""
        return iter(())

    def visit_abstraction(self, abstraction: terms.Abstraction[str]) -> Iterator[terms.Abstraction[str]]:
        """visit an Abstraction term"""
        results = abstraction.body.accept(self)
        return map(lambda b: terms.Abstraction(abstraction.bound, b), results)

    def visit_application(self, application: terms.Application[str]) -> Iterator[terms.Term[str]]:
        """visit an Application term"""
        match application.abstraction:
            # normal order dictates we reduce leftmost outermost redex first
            case terms.Abstraction(bound, body):
                reduced = body.accept(CountingSubstitutingVisitor(bound, application.argument))
                yield reduced
                yield from reduced.accept(self)
            case _:
                # try to reduce the abstraction until this is a redex
                abstraction = application.abstraction
                for transformation in application.abstraction.accept(self):
                    yield terms.Application(transformation, application.argument)
                    match transformation:
                        case terms.Abstraction(bound, body):
                            reduced = body.accept(
                                CountingSubstitutingVisitor(bound, application.argument)
                            )
                            yield reduced
                            yield from reduced.accept(self)
                            return
                        case _:
                            abstraction = transformation
                # no redex, continue with argument
                transformations = application.argument.accept(self)
                yield from map(lambda a: terms.Application(abstraction, a), transformations)
