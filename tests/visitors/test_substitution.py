#!/usr/bin/python3

"""Tests for variable substitution"""

from unittest import TestCase
from lambda_calculus.terms import Variable, Abstraction, Application
from lambda_calculus.errors import CollisionError
from lambda_calculus.visitors import substitution


class SubstitutingVisitorTest(TestCase):
    """Test for Visitor substituting a free variable"""

    visitor: substitution.SubstitutingVisitor[int]

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = substitution.SubstitutingVisitor(1, Variable(42))

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


class TestCountingSubstitutingVisitor(TestCase):
    """Test for Visitor substituting a free variable without errors"""

    visitor: substitution.CountingSubstitutingVisitor

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = substitution.CountingSubstitutingVisitor("a", Variable("x"))

    def test_location(self) -> None:
        """test if the right variables get substituted"""
        self.assertEqual(
            Variable("b").accept(self.visitor),
            Variable("b")
        )
        self.assertEqual(
            Variable("a").accept(self.visitor),
            Variable("x")
        )
        self.assertEqual(
            Application(
                Abstraction("a", Variable("a")),
                Abstraction("b", Variable("a"))
            ).accept(self.visitor),
            Application(Abstraction("a", Variable("a")), Abstraction("b", Variable("x")))
        )

    def test_renaming(self) -> None:
        """test if colliding bound variables get renamed"""
        self.assertEqual(
            Abstraction("x", Variable("a")).accept(self.visitor),
            Abstraction("x1", Variable("x"))
        )
        self.assertEqual(
            Abstraction("x", Abstraction("x1", Variable("a"))).accept(self.visitor),
            Abstraction("x2", Abstraction("x1", Variable("x")))
        )
        self.assertEqual(
            Abstraction("x", Application(Variable("a"), Variable("x1"))).accept(self.visitor),
            Abstraction("x2", Application(Variable("x"), Variable("x1")))
        )
        self.assertEqual(
            Abstraction(
                "x",
                Application(
                    Abstraction("x", Variable("x")),
                    Variable("a")
                )
            ).accept(self.visitor),
            Abstraction(
                "x1",
                Application(
                    Abstraction("x1", Variable("x1")),
                    Variable("x")
                )
            )
        )
