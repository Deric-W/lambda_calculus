#!/usr/bin/python3

"""Tests for arithmetic terms"""

from unittest import TestCase
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor
from lambda_calculus.terms import Application, arithmetic


class OrderingTest(TestCase):
    """Test for ordering functions"""

    visitor: BetaNormalisingVisitor

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = BetaNormalisingVisitor()

    def test_successor(self) -> None:
        """test successor term"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application(arithmetic.SUCCESSOR, arithmetic.number(8))
            ),
            arithmetic.number(9)
        )

    def test_predecessor(self) -> None:
        """test predecessor term"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application(arithmetic.PREDECESSOR, arithmetic.number(8))
            ),
            arithmetic.number(7)
        )

    def test_predecessor_zero(self) -> None:
        """test predecessor of zero"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application(arithmetic.PREDECESSOR, arithmetic.number(0))
            ),
            arithmetic.number(0)
        )


class CalculationsTest(TestCase):
    """Test for calculations with natural numbers"""

    visitor: BetaNormalisingVisitor

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = BetaNormalisingVisitor()

    def test_add(self) -> None:
        """test addition term"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    arithmetic.ADD,
                    (arithmetic.number(3), arithmetic.number(5))
                )
            ),
            arithmetic.number(8)
        )

    def test_subtract(self) -> None:
        """test subtraction term"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    arithmetic.SUBTRACT,
                    (arithmetic.number(10), arithmetic.number(3))
                )
            ),
            arithmetic.number(7)
        )

    def test_subtract_greater(self) -> None:
        """test subtraction below zero"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    arithmetic.SUBTRACT,
                    (arithmetic.number(10), arithmetic.number(13))
                )
            ),
            arithmetic.number(0)
        )

    def test_multiply(self) -> None:
        """test multiplication term"""
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    arithmetic.MULTIPLY,
                    (arithmetic.number(5), arithmetic.number(2))
                )
            ),
            arithmetic.number(10)
        )

    def test_power(self) -> None:
        """test power term"""
        # alpha conversion needed
        nine = arithmetic.number(9)
        nine = nine.replace(body=nine.body.alpha_conversion("x1"))
        nine = nine.alpha_conversion("x")
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    arithmetic.POWER,
                    (arithmetic.number(3), arithmetic.number(2))
                )
            ),
            nine
        )

    def test_power_zero(self) -> None:
        """test power zero"""
        one = self.visitor.skip_intermediate(
            Application.with_arguments(
                arithmetic.POWER,
                (arithmetic.number(5), arithmetic.number(0))
            )
        )
        # eta conversion needed
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    arithmetic.ADD,
                    (one, arithmetic.number(3))
                )
            ),
            arithmetic.number(4)
        )
        # alpha conversion needed
        zero = arithmetic.number(0)
        zero = zero.replace(body=zero.body.alpha_conversion("x1"))
        zero = zero.alpha_conversion("x")
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application.with_arguments(
                    arithmetic.POWER,
                    (arithmetic.number(0), arithmetic.number(5))
                )
            ),
            zero
        )
