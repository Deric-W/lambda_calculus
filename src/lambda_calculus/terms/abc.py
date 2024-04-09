#!/usr/bin/python3

"""Predefined Variables for all ASCII letters"""

from string import ascii_letters
from . import Variable

__all__ = tuple(ascii_letters)

# better IDE autocompletion
a, b, c, d, e, f, g, h, i, j = map(Variable, "abcdefghij")
k, l, m, n, o, p, q, r, s, t = map(Variable, "klmnopqrst")
u, v, w, x, y, z = map(Variable, "uvwxyz")

A, B, C, D, E, F, G, H, I, J = map(Variable, "ABCDEFGHIJ")
K, L, M, N, O, P, Q, R, S, T = map(Variable, "KLMNOPQRST")
U, V, W, X, Y, Z = map(Variable, "UVWXYZ")
