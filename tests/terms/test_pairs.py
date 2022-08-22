#!/usr/bin/python3

"""Tests for pair terms"""

from unittest import TestCase
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor
from lambda_calculus.terms import Term, Variable, Application, pairs
from lambda_calculus.terms.logic import TRUE, FALSE


class PairTest(TestCase):
    """Test for pair terms"""

    visitor: BetaNormalisingVisitor

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = BetaNormalisingVisitor()

    def make_pair(self, a: Term[str], b: Term[str]) -> Term[str]:
        """make a pair (a, b)"""
        return Application.with_arguments(pairs.PAIR, (a, b))

    def test_first(self) -> None:
        """test accessing the first element"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application(
                    pairs.FIRST,
                    self.make_pair(Variable("a"), Variable("b"))
                )
            ),
            Variable("a")
        )

    def test_second(self) -> None:
        """test accessing rhe second element"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application(
                    pairs.SECOND,
                    self.make_pair(Variable("a"), Variable("b"))
                )
            ),
            Variable("b")
        )

    def test_null(self) -> None:
        """test check for NIL pair"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application(pairs.NULL, pairs.NIL)
            ),
            TRUE
        )
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application(
                    pairs.NULL,
                    self.make_pair(Variable("a"), Variable("b"))
                )
            ),
            FALSE
        )
