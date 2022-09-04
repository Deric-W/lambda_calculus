#!/usr/bin/python3

"""Tests for variable substitution checking for bound free variables"""

from unittest import TestCase
from lambda_calculus.terms import Variable, Abstraction, Application
from lambda_calculus.errors import CollisionError
from lambda_calculus.visitors.substitution import checked


class CheckedSubstitutionTest(TestCase):
    """Tests for variable substitution checking for bound free variables"""

    visitor: checked.CheckedSubstitution[int]

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = checked.CheckedSubstitution.from_substitution(1, Variable(42))

    def test_location(self) -> None:
        """test if the right variables get substituted"""
        self.assertEqual(
            Variable(2).accept(self.visitor),
            Variable(2)
        )
        self.assertEqual(
            Variable(1).accept(self.visitor),
            Variable(42)
        )
        self.assertEqual(
            Application(
                Abstraction(1, Variable(1)),
                Abstraction(2, Variable(1))
            ).accept(self.visitor),
            Application(Abstraction(1, Variable(1)), Abstraction(2, Variable(42)))
        )

    def test_lazy_bound_check(self) -> None:
        """test if free variables can be bound if they are not substituted"""
        self.assertEqual(
            Abstraction(42, Variable(2)).accept(self.visitor),
            Abstraction(42, Variable(2))
        )

    def test_collision(self) -> None:
        """test if collisions are detected"""
        with self.assertRaises(CollisionError):
            Abstraction(42, Variable(1)).accept(self.visitor)
        with self.assertRaises(CollisionError):
            Abstraction(
                42,
                Application(Abstraction(42, Variable(2)), Variable(1))
            ).accept(self.visitor)

    def test_reuse(self) -> None:
        """test if the visitor can be reused"""
        self.assertEqual(
            Abstraction(42, Variable(2)).accept(self.visitor),
            Abstraction(42, Variable(2))
        )
        self.assertEqual(self.visitor.bound_variables, {})
        with self.assertRaises(CollisionError):
            Abstraction(42, Variable(1)).accept(self.visitor)
        self.assertEqual(self.visitor.bound_variables, {})
