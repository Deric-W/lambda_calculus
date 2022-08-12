#!/usr/bin/python3

"""Tests for the Term implementations"""

from unittest import TestCase
from lambda_calculus import Variable, Abstraction, Application
from lambda_calculus.errors import CollisionError


class StrWrapper:
    """Wrapper with custom string representation"""

    representation: str

    def __init__(self, representation: str) -> None:
        self.representation = representation

    def __str__(self) -> str:
        return self.representation


class VariableTest(TestCase):
    """Test for Term consisting of one variable"""

    def test_valid_name(self) -> None:
        """test invalid name detection"""
        for name in (42, "test"):
            self.assertEqual(Variable.with_valid_name(name), Variable(name))
        for name in ("a b", ")a", "b(", " ", "λa.b", ""):
            with self.assertRaises(ValueError):
                Variable.with_valid_name(name)
            with self.assertRaises(ValueError):
                Variable.with_valid_name(StrWrapper(name))

    def test_str(self) -> None:
        """test string representation"""
        for name in (42, "test"):
            self.assertEqual(str(Variable(name)), str(name))

    def test_free_variables(self) -> None:
        """test free variables"""
        self.assertEqual(Variable(42).free_variables(), {42})

    def test_bound_variables(self) -> None:
        """test bound variables"""
        self.assertEqual(Variable(42).bound_variables(), set())

    def test_is_beta_normal_form(self) -> None:
        """test beta normal form detection"""
        self.assertTrue(Variable(42).is_beta_normal_form())


class AbstractionTest(TestCase):
    """Tests for Term consisting of an abstraction"""

    def test_curried(self) -> None:
        """test curried representation"""
        self.assertEqual(
            Abstraction.curried((1, 2, 3), Variable(3)),
            Abstraction(1, Abstraction(2, Abstraction(3, Variable(3))))
        )
        with self.assertRaises(ValueError):
            Abstraction.curried([], Variable(3))

    def test_str(self) -> None:
        """test string representation"""
        self.assertEqual(
            str(Abstraction(4, Variable(4))),
            "(λ4.4)"
        )

    def test_free_variables(self) -> None:
        """test free variables"""
        combinator = Abstraction(1, Variable(1))
        self.assertTrue(combinator.is_combinator())
        self.assertEqual(combinator.free_variables(), set())
        self.assertEqual(Abstraction(2, combinator).free_variables(), set())
        self.assertEqual(Abstraction(1, Variable(2)).free_variables(), {2})

    def test_bound_variables(self) -> None:
        """test bound variables"""
        combinator = Abstraction(1, Variable(1))
        self.assertEqual(combinator.bound_variables(), {1})
        self.assertEqual(Abstraction(2, combinator).bound_variables(), {2, 1})
        self.assertEqual(Abstraction(1, Variable(2)).bound_variables(), {1})

    def test_is_beta_normal_form(self) -> None:
        """test beta normal form detection"""
        combinator = Abstraction(1, Variable(1))
        self.assertTrue(combinator.is_beta_normal_form())
        self.assertFalse(Abstraction(1, Application(combinator, Variable(1))).is_beta_normal_form())

    def test_alpha_conversion(self) -> None:
        """test alpha conversion"""
        self.assertEqual(
            Abstraction(1, Abstraction(1, Variable(1))).alpha_conversion(2),
            Abstraction(2, Abstraction(1, Variable(1)))
        )
        self.assertEqual(
            Abstraction(1, Abstraction(2, Application(Variable(1), Variable(2)))).alpha_conversion(3),
            Abstraction(3, Abstraction(2, Application(Variable(3), Variable(2))))
        )
        self.assertEqual(
            Abstraction(1, Application(Abstraction(2, Application(Variable(3), Variable(4))), Variable(1))).alpha_conversion(2),
            Abstraction(2, Application(Abstraction(2, Application(Variable(3), Variable(4))), Variable(2)))
        )
        self.assertEqual(
            Abstraction(1, Application(Abstraction(2, Application(Variable(3), Variable(2))), Variable(1))).alpha_conversion(2),
            Abstraction(2, Application(Abstraction(2, Application(Variable(3), Variable(2))), Variable(2)))
        )
        self.assertEqual(
            Abstraction(1, Application(Abstraction(1, Application(Variable(3), Variable(1))), Variable(1))).alpha_conversion(2),
            Abstraction(2, Application(Abstraction(1, Application(Variable(3), Variable(1))), Variable(2)))
        )
        with self.assertRaises(CollisionError):
            Abstraction(1, Abstraction(2, Application(Variable(1), Variable(2)))).alpha_conversion(2)
        with self.assertRaises(CollisionError):
            Abstraction(1, Abstraction(2, Application(Abstraction(2, Variable(2)), Variable(1)))).alpha_conversion(2)

    def test_eta_reduction(self) -> None:
        """test eta reduction"""
        self.assertEqual(
            Abstraction(1, Application(Variable(2), Variable(1))).eta_reduction(),
            Variable(2)
        )
        with self.assertRaises(ValueError):
            Abstraction(1, Variable(1)).eta_reduction()
        with self.assertRaises(ValueError):
            Abstraction(1, Application(Variable(2), Variable(3))).eta_reduction()
        with self.assertRaises(ValueError):
            Abstraction(1, Application(Variable(1), Variable(1))).eta_reduction()


class ApplicationTest(TestCase):
    """Tests for Term consisting of an application"""

    def test_with_arguments(self) -> None:
        """test Application with multiple arguments"""
        combinator = Abstraction(1, Variable(1))
        self.assertEqual(
            Application.with_arguments(Abstraction(2, combinator), (Variable(3), Variable(4))),
            Application(Application(Abstraction(2, combinator), Variable(3)), Variable(4))
        )
        with self.assertRaises(ValueError):
            Application.with_arguments(Abstraction(2, combinator), [])

    def test_str(self) -> None:
        """test string representation"""
        self.assertEqual(
            str(Application(Variable(1), Variable(2))),
            "(1 2)"
        )

    def test_free_variables(self) -> None:
        """test free variables"""
        self.assertEqual(Application(Variable(1), Variable(2)).free_variables(), {1, 2})
        self.assertEqual(Application(Variable(1), Variable(1)).free_variables(), {1})
        self.assertEqual(Application(Abstraction(1, Variable(1)), Variable(2)).free_variables(), {2})
        self.assertEqual(Application(Abstraction(1, Variable(1)), Abstraction(2, Variable(2))).free_variables(), set())

    def test_bound_variables(self) -> None:
        """test bound variables"""
        self.assertEqual(Application(Variable(1), Variable(2)).bound_variables(), set())
        self.assertEqual(Application(Abstraction(1, Variable(1)), Abstraction(2, Variable(2))).bound_variables(), {1, 2})

    def test_is_beta_normal_form(self) -> None:
        """test beta normal form detection"""
        combinator = Abstraction(1, Variable(1))
        self.assertTrue(Application(Variable(1), Variable(2)).is_beta_normal_form())
        self.assertTrue(Application(Variable(3), combinator).is_beta_normal_form())
        self.assertFalse(Application(combinator, Variable(3)).is_beta_normal_form())
        self.assertFalse(Application(Variable(1), Application(combinator, Variable(3))).is_beta_normal_form())

    def test_beta_reduction(self) -> None:
        """test beta reduction"""
        self.assertEqual(
            Application(Abstraction(1, Abstraction(2, Variable(1))), Variable(3)).beta_reduction(),
            Abstraction(2, Variable(3))
        )
        self.assertEqual(
            Application(Abstraction(1, Abstraction(1, Variable(1))), Variable(3)).beta_reduction(),
            Abstraction(1, Variable(1))
        )
        self.assertEqual(
            Application(Abstraction(1, Abstraction(2, Variable(3))), Variable(2)).beta_reduction(),
            Abstraction(2, Variable(3))
        )
        with self.assertRaises(ValueError):
            Application(Variable(1), Variable(2)).beta_reduction()
        with self.assertRaises(CollisionError):
            Application(Abstraction(1, Abstraction(2, Variable(1))), Variable(2)).beta_reduction()
