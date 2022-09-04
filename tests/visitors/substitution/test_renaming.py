#!/usr/bin/python3

"""Test for Visitor substituting a free variable without errors"""

from unittest import TestCase
from collections.abc import Generator, Iterable
from itertools import count
from lambda_calculus.terms import Variable, Abstraction, Application
from lambda_calculus.visitors.substitution import renaming


class CountingSubstitutionTest(TestCase):
    """Test for Visitor substituting a free variable without errors"""

    visitor: renaming.CountingSubstitution

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = renaming.CountingSubstitution.from_substitution("a", Variable("x"))

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


class TracingDecoratorTest(TestCase):
    """Tests for transforming a RenamingSubstitution into an Generator"""

    visitor: renaming.TracingDecorator[str]

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = renaming.CountingSubstitution.from_substitution("a", Variable("x")).trace()

    def assertGenerator(self, generator: Generator[object, None, object], outputs: Iterable[object], result: object) -> None:
        """assert that a generator produces the correct output and result"""
        outputs = iter(outputs)
        for number in count(start=1):
            try:
                output = next(generator)
            except StopIteration as stop:
                with self.assertRaises(StopIteration, msg="generator produced fewer outputs"):
                    next(outputs)
                self.assertEqual(stop.value, result, "generator return value was different")
                break
            try:
                value = next(outputs)
            except StopIteration:
                self.fail("generator produced more outputs")
            self.assertEqual(output, value, f"output no. {number} was different")

    def test_empty(self) -> None:
        """test behavior when substituting not existing variable"""
        term = Variable("x").abstract("z").apply_to(Variable("b"))
        self.assertGenerator(
            self.visitor.visit(term),
            (),
            term
        )

    def test_variable(self) -> None:
        """test visiting a variable term"""
        self.assertGenerator(
            self.visitor.visit(Variable("b")),
            (),
            Variable("b")
        )
        self.assertGenerator(
            self.visitor.visit(Variable("a")),
            (),
            Variable("x")
        )

    def test_abstraction(self) -> None:
        """test visiting an abstraction term"""
        term = Variable("b").abstract("c")
        self.assertGenerator(
            self.visitor.visit(term),
            (),
            term
        )
        term = Variable("a").abstract("c")
        self.assertGenerator(
            self.visitor.visit(term),
            (),
            Variable("x").abstract("c")
        )
        term = Variable("a").apply_to(Variable("x")).abstract("x").abstract("x")
        self.assertGenerator(
            self.visitor.visit(term),
            (
                Variable("a").apply_to(Variable("x")).abstract("x").abstract("x1"),
                Variable("a").apply_to(Variable("x1")).abstract("x1").abstract("x1")
            ),
            Variable("x").apply_to(Variable("x1")).abstract("x1").abstract("x1")
        )
        term = Variable("a").abstract("a")
        self.assertGenerator(
            self.visitor.visit(term),
            (),
            term
        )

    def test_application(self) -> None:
        """test visiting an application term"""
        term = Variable("b").apply_to(Variable("c"))
        self.assertGenerator(
            self.visitor.visit(term),
            (),
            term
        )
        term = Variable("a").apply_to(Variable("b"))
        self.assertGenerator(
            self.visitor.visit(term),
            (),
            Variable("x").apply_to(Variable("b"))
        )
        term = Variable("a").abstract("a").apply_to(Variable("a"))
        self.assertGenerator(
            self.visitor.visit(term),
            (),
            Variable("a").abstract("a").apply_to(Variable("x"))
        )
        term = Variable("a") \
                .apply_to(Variable("x")) \
                .abstract("x") \
                .apply_to(Variable("a").abstract("a"))
        self.assertGenerator(
            self.visitor.visit(term),
            (
                Variable("a")
                    .apply_to(Variable("x1"))
                    .abstract("x1")
                    .apply_to(Variable("a").abstract("a")),
            ),
            Variable("x")
                .apply_to(Variable("x1"))
                .abstract("x1")
                .apply_to(Variable("a").abstract("a"))
        )
