#!/usr/bin/python3

"""Tests for logic terms"""

from unittest import TestCase
from collections.abc import Iterable, Iterator
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor
from lambda_calculus.terms import Term, Variable, Application, logic


class LogicTest(TestCase):
    """Test for logic terms"""

    visitor: BetaNormalisingVisitor

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = BetaNormalisingVisitor()

    def make_truth_table(self, outputs: Iterable[Term[str]]) -> Iterator[tuple[tuple[Term[str], Term[str]], Term[str]]]:
        """make a truth table with two inputs"""
        inputs = (
            (logic.FALSE, logic.FALSE),
            (logic.TRUE, logic.FALSE),
            (logic.FALSE, logic.TRUE),
            (logic.TRUE, logic.TRUE)
        )
        return zip(inputs, outputs)

    def test_and(self) -> None:
        """test logical and"""
        for (a, b), c in self.make_truth_table((logic.FALSE,) * 3 + (logic.TRUE,)):
            self.assertEqual(
                self.visitor.skip_intermediate(
                    Application.with_arguments(logic.AND, (a, b))
                ),
                c
            )

    def test_or(self) -> None:
        """test logical or"""
        for (a, b), c in self.make_truth_table((logic.FALSE,) + (logic.TRUE,) * 3):
            self.assertEqual(
                self.visitor.skip_intermediate(
                    Application.with_arguments(logic.OR, (a, b))
                ),
                c
            )

    def test_not(self) -> None:
        """test logical negation"""
        self.assertEqual(
            self.visitor.skip_intermediate(Application(logic.NOT, logic.TRUE)),
            logic.FALSE
        )
        self.assertEqual(
            self.visitor.skip_intermediate(Application(logic.NOT, logic.FALSE)),
            logic.TRUE
        )

    def test_if_then_else(self) -> None:
        """test if statement"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    logic.IF_THEN_ELSE,
                    (logic.TRUE, Variable("a"), Variable("b"))
                )
            ),
            Variable("a")
        )
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    logic.IF_THEN_ELSE,
                    (logic.FALSE, Variable("a"), Variable("b"))
                )
            ),
            Variable("b")
        )
