#!/usr/bin/python3

"""Visitor for term normalisation"""

from __future__ import annotations
from collections.abc import Iterator
from enum import Enum, unique
from typing import TypeVar, final, Generator, TypeAlias
from .. import terms
from . import Visitor
from .substitution.renaming import CountingSubstitution

__all__ = (
    "Conversion",
    "BetaNormalisingVisitor",
)

V = TypeVar("V")

Step: TypeAlias = tuple["Conversion", terms.Term[str]]


@unique
class Conversion(Enum):
    """
    Conversion performed by normalisation
    """
    ALPHA = 0
    BETA = 1


@final
class BetaNormalisingVisitor(Visitor[Iterator[Step], str]):
    """
    Visitor which transforms a term into its beta normal form,
    yielding intermediate steps until it is reached

    No steps are yielded if the term is already in its beta normal form.

    Remember that some terms dont thave a beta normal form and
    can cause infinite recursion.
    """

    __slots__ = ()

    def skip_intermediate(self, term: terms.Term[str]) -> terms.Term[str]:
        """
        Calculate the beta normal form directly.
        
        :param term: term which should be transformed into ist beta normal form
        :return: new term representing the beta normal form if it exists
        """
        result = term
        for _, intermediate in term.accept(self):
            result = intermediate
        return result

    def visit_variable(self, variable: terms.Variable[str]) -> Iterator[Step]:
        """
        Visit a Variable term.

        :param variable: variable term to visit
        :return: empty Iterator, variables are already in beta normal form
        """
        return iter(())

    def visit_abstraction(self, abstraction: terms.Abstraction[str]) -> Iterator[Step]:
        """
        Visit an Abstraction term.

        :param abstraction: abstraction term to visit
        :return: Iterator yielding steps performed on its body
        """
        results = abstraction.body.accept(self)
        return map(lambda s: (s[0], terms.Abstraction(abstraction.bound, s[1])), results)

    def beta_reducation(self, abstraction: terms.Abstraction[str], argument: terms.Term[str]) -> Generator[Step, None, terms.Term[str]]:
        """
        Perform beta reduction of an application.
        
        :param abstraction: abstraction of the application
        :param argument: argument of the application
        :return: Generator yielding steps and returning the reduced term
        """
        conversions = CountingSubstitution.from_substitution(abstraction.bound, argument).trace()
        reduced = yield from map(
            lambda body: (
                Conversion.ALPHA,
                terms.Application(terms.Abstraction(abstraction.bound, body), argument)
            ),
            abstraction.body.accept(conversions)    # type: ignore
        )
        yield (Conversion.BETA, reduced)
        return reduced      # type: ignore

    def visit_application(self, application: terms.Application[str]) -> Iterator[Step]:
        """
        Visit an Application term

        The abstraction and argument are not automatically visited.

        :param application: application term to visit
        :return: steps for performing beta reduction if possible
                 and performed on its result or abstraction and argument
        """
        if isinstance(application.abstraction, terms.Abstraction):
            # normal order dictates we reduce the leftmost outermost redex first
            reduced = yield from self.beta_reducation(application.abstraction, application.argument)
            yield from reduced.accept(self)
        else:
            # try to reduce the abstraction until this is a redex
            abstraction = application.abstraction
            for conversion, transformation in application.abstraction.accept(self):
                yield (conversion, terms.Application(transformation, application.argument))
                if isinstance(transformation, terms.Abstraction):
                    reduced = yield from self.beta_reducation(transformation, application.argument)
                    yield from reduced.accept(self)
                    return
                else:
                    abstraction = transformation
            # no redex, continue with argument
            transformations = application.argument.accept(self)
            yield from map(lambda s: (s[0], terms.Application(abstraction, s[1])), transformations)
