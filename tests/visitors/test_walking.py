#!/usr/bin/python3

"""Tests for term walking"""

from unittest import TestCase
from lambda_calculus.terms import Variable, Abstraction, Application
from lambda_calculus.visitors import walking


class DepthFirstVisitorTest(TestCase):
    """Test for Visitor yielding subterms depth first"""

    visitor: walking.DepthFirstVisitor[int]

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = walking.DepthFirstVisitor()

    def test_order(self) -> None:
        """test subterm ordering"""
        self.assertEqual(
            list(Variable(1)),
            [Variable(1)]
        )
        self.assertEqual(
            list(
                Application(
                    Abstraction(1, Variable(1)),
                    Abstraction(2, Abstraction(3, Variable(2)))
                )
            ),
            [
                Variable(1),
                Abstraction(1, Variable(1)),
                Variable(2),
                Abstraction(3, Variable(2)),
                Abstraction(2, Abstraction(3, Variable(2))),
                Application(
                    Abstraction(1, Variable(1)),
                    Abstraction(2, Abstraction(3, Variable(2)))
                )
            ]
        )

    def test_shared(self) -> None:
        """test handling of shared subterms"""
        shared = Abstraction(3, Variable(2))
        self.assertEqual(
            list(Application(shared, shared)),
            [
                Variable(2),
                shared,
                Variable(2),
                shared,
                Application(shared, shared)
            ]
        )
