#!/usr/bin/python3

"""Tests for combinator terms"""

from unittest import TestCase
from lambda_calculus.terms import Variable, combinators
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor


class CombinatorTest(TestCase):
    """Tests for combinator terms"""

    def test_is_combinator(self) -> None:
        """test that all terms a combinators"""
        for name in combinators.__all__:
            self.assertTrue(getattr(combinators, name).is_combinator())

    def test_y(self) -> None:
        """test Y combinator"""
        self.assertEqual(
            BetaNormalisingVisitor().skip_intermediate(
                combinators.Y.apply_to(combinators.K.apply_to(Variable("a")))
            ),
            Variable("a")
        )

    def test_s(self) -> None:
        """test S combinator"""
        term = Variable("a")
        self.assertEqual(
            BetaNormalisingVisitor().skip_intermediate(
                combinators.S.apply_to(combinators.K, Variable("b"), term)
            ),
            term
        )

    def test_k(self) -> None:
        """test K combinator"""
        term = Variable("a")
        self.assertEqual(
            BetaNormalisingVisitor().skip_intermediate(
                combinators.K.apply_to(term, Variable("b"))
            ),
            term
        )

    def test_i(self) -> None:
        """test I combinator"""
        term = Variable("a")
        self.assertEqual(
            BetaNormalisingVisitor().skip_intermediate(
                combinators.I.apply_to(term)
            ),
            term
        )

    def test_b(self) -> None:
        """test B combinator"""
        self.assertEqual(
            BetaNormalisingVisitor().skip_intermediate(
                combinators.B.apply_to(
                    combinators.K.apply_to(Variable("b")),
                    combinators.K.apply_to(Variable("c")),
                    Variable("a")
                )
            ),
            Variable("b")
        )

    def test_c(self) -> None:
        """test C combinator"""
        self.assertEqual(
            BetaNormalisingVisitor().skip_intermediate(
                combinators.C.apply_to(combinators.I, Variable("a"), Variable("b"))
            ),
            Variable("b").apply_to(Variable("a"))
        )

    def test_w(self) -> None:
        """test W combinator"""
        self.assertEqual(
            BetaNormalisingVisitor().skip_intermediate(
                combinators.W.apply_to(combinators.I, Variable("a"))
            ),
            Variable("a").apply_to(Variable("a"))
        )

    def test_omega(self) -> None:
        """test Omega combinator"""
        for index, (_, step) in enumerate(BetaNormalisingVisitor().visit(combinators.OMEGA)):
            if index < 10:
                self.assertEqual(step, combinators.OMEGA)
            else:
                break
        else:
            self.fail("reached beta normal form")
