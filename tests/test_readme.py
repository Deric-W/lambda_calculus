#!/usr/bin/python3

"""Tests for README examples"""

from unittest import TestCase
from lambda_calculus import Variable, Abstraction, Application
from lambda_calculus.terms import Term
from lambda_calculus.visitors.normalisation import BetaNormalisingVisitor


class ExampleTest(TestCase):
    """Test for README example"""

    term: Application[str]

    def setUp(self) -> None:
        """create a reference term"""
        term: Term[str] = Application(Variable("+"), Variable("x"))
        term = Application(term, Variable("y"))
        term = Abstraction("y", term)
        term = Abstraction("x", term)
        term = Application(term, Variable("y"))
        term = Application(term, Variable("3"))
        term = Abstraction("y", term)
        self.term = Application(term, Variable("4"))

    def test_nesting(self) -> None:
        """test nesting example"""
        term: Term[str] = Application(Variable("+"), Variable("x"))
        term = Application(term, Variable("y"))
        term = Abstraction("y", term)
        term = Abstraction("x", term)
        term = Application(term, Variable("y"))
        term = Application(term, Variable("3"))
        term = Abstraction("y", term)
        term = Application(term, Variable("4"))
        self.assertEqual(term, self.term)

    def test_utility_methods(self) -> None:
        """test utility method example"""
        x = Variable.with_valid_name("x")
        y = Variable.with_valid_name("y")
        term: Term[str] = Application.with_arguments(Variable.with_valid_name("+"), (x, y))
        term = Abstraction.curried(("x", "y"), term)
        term = Application.with_arguments(term, (y, Variable.with_valid_name("3")))
        term = Abstraction("y", term)
        term = Application(term, Variable.with_valid_name("4"))
        self.assertEqual(term, self.term)

    def test_method_chaining(self) -> None:
        """test method chaining example"""
        x = Variable.with_valid_name("x")
        y = Variable.with_valid_name("y")
        term = Variable("+") \
            .apply_to(x, y) \
            .abstract("x", "y") \
            .apply_to(y, Variable("3")) \
            .abstract("y") \
            .apply_to(Variable("4"))
        self.assertEqual(term, self.term)

    def test_evaluation(self) -> None:
        """test evaluation example"""
        self.assertEqual(
            BetaNormalisingVisitor().skip_intermediate(self.term),
            Application.with_arguments(
                Variable("+"),
                (Variable("4"), Variable("3"))
            )
        )
