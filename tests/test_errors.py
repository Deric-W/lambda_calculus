#!/usr/bin/python3

"""Tests for custom errors"""

from unittest import TestCase
from lambda_calculus import errors


class CollisionErrorTest(TestCase):
    """Tests for Exception thrown when a variable already exists"""

    def test_exception(self) -> None:
        """test exception subclass"""
        exception: Exception = errors.CollisionError("test", [])
        self.assertIsInstance(exception, ValueError)
        self.assertEqual(exception.args, ("test", []))

    def test_repr(self) -> None:
        """test string representation"""
        exception: Exception = errors.CollisionError("test", [])
        self.assertEqual(
            repr(exception),
            f"lambda_calculus.errors.CollisionError({'test'!r}, {[]!r})"
        )

    def test_str(self) -> None:
        """test exception message"""
        self.assertEqual(
            str(errors.CollisionError("test", [])),
            "[collisions: none] test"
        )
        self.assertEqual(
            str(errors.CollisionError("test", range(3))),
            "[collisions: 0, 1, 2] test"
        )
