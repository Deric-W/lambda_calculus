#!/usr/bin/python3

"""Tests for the predefined variables"""

from unittest import TestCase
from string import ascii_letters
from lambda_calculus.terms import Variable, abc


class PredefinedVariablesTest(TestCase):
    """Tests for the predefined variables"""

    def test_complete(self) -> None:
        """Check whether all letters exist"""
        self.assertEqual(tuple(ascii_letters), abc.__all__)
        for letter in ascii_letters:
            self.assertTrue(hasattr(abc, letter))

    def test_variables(self) -> None:
        """Test the predefined variables"""
        for letter in ascii_letters:
            variable = getattr(abc, letter)
            self.assertIsInstance(variable, Variable)
            self.assertEqual(variable.name, letter)
