#!/usr/bin/python3

"""Tests for term normalisation"""

from unittest import TestCase
from lambda_calculus.terms import Variable, Abstraction, Application
from lambda_calculus.visitors import normalisation


class TestBetaNormalisingVisitor(TestCase):
    """Test for Visitor which transforms a term to beta normal form"""

    visitor: normalisation.BetaNormalisingVisitor

    def setUp(self) -> None:
        """create a visitor"""
        self.visitor = normalisation.BetaNormalisingVisitor()

    def test_normal_form(self) -> None:
        """test behavior with terms already in beta normal form"""
        terms = (
            Variable("a"),
            Abstraction("a", Variable("a")),
            Application(
                Variable("a"),
                Abstraction("a", Variable("a"))
            )
        )
        for term in terms:
            self.assertEqual(list(term.accept(self.visitor)), [])

    def test_reduction(self) -> None:
        """test that beta normal form is reached"""
        x = Variable("x")
        y = Variable("y")
        t = Application.with_arguments(Variable("+"), (x, y))
        t = Abstraction.curried(("x", "y"), t)
        t = Application.with_arguments(t, (y, Variable("3")))
        t = Abstraction("y", t)
        term = Application(t, Variable("4"))
        steps = [(normalisation.Conversion.BETA, term.beta_reduction())]
        steps.append(
            (
                normalisation.Conversion.BETA,
                steps[-1][1].replace(abstraction=steps[0][1].abstraction.beta_reduction())
            )
        )
        steps.append(
            (
                normalisation.Conversion.BETA,
                steps[-1][1].beta_reduction()
            )
        )
        self.assertEqual(
            list(term.accept(self.visitor)),
            steps
        )
        self.assertTrue(steps[-1][1].is_beta_normal_form())

    def test_order(self) -> None:
        """test that normal order is maintained"""
        triple = Abstraction(
            "w",
            Application.with_arguments(
                Variable("w"),
                [Variable("w")] * 2
            )
        )
        self.assertEqual(
            list(
                Application(
                    Application(
                        Abstraction("a", Variable("a")),
                        Abstraction("x", Variable("z"))
                    ),
                    Application(
                        triple,
                        triple
                    )
                ).accept(self.visitor)
            ),
            [
                (
                    normalisation.Conversion.BETA,
                    Application(
                        Abstraction("x", Variable("z")),
                        Application(
                            triple,
                            triple
                        )
                    )
                ),
                (
                    normalisation.Conversion.BETA,
                    Variable("z")
                )
            ]
        )

    def test_collision(self) -> None:
        """test that collisions are renamed"""
        problem = Application(
            Variable("x").apply_to(Variable("x")).abstract("x"),
            Variable("a").apply_to(Variable("b")).abstract("a", "b")
        )
        steps = [(normalisation.Conversion.BETA, problem.beta_reduction())]
        steps.append((normalisation.Conversion.BETA, steps[-1][1].beta_reduction()))
        steps.append(
            (
                normalisation.Conversion.ALPHA,
                Variable("a").apply_to(Variable("b1")).abstract("a", "b1").apply_to(Variable("b")).abstract("b")
            )
        )
        steps.append(
            (
                normalisation.Conversion.BETA,
                Variable("b").apply_to(Variable("b1")).abstract("b", "b1")
            )
        )
        self.assertEqual(
            list(problem.accept(self.visitor)),
            steps
        )
        self.assertTrue(steps[-1][1].is_beta_normal_form())

    def test_no_normal_form(self) -> None:
        """test behavior when no normal form exists"""
        double = Abstraction("x", Application(Variable("x"), Variable("x")))
        term = Application(double, double)
        for iteration, (conversion, transformation) in enumerate(term.accept(self.visitor)):
            if iteration > 10:
                break
            self.assertIs(conversion, normalisation.Conversion.BETA)
            self.assertEqual(transformation, term)

    def test_skip_intermediate(self) -> None:
        """test skipping of intermediate results"""
        self.assertEqual(
            self.visitor.skip_intermediate(Abstraction("a", Variable("z"))),
            Abstraction("a", Variable("z"))
        )
        self.assertEqual(
            self.visitor.skip_intermediate(
                Application(Abstraction("a", Variable("a")), Variable("z"))
            ),
            Variable("z")
        )
