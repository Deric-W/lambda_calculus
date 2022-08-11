#!/usr/bin/python3

"""Errors raised by Term operations"""

from __future__ import annotations
from collections.abc import Collection

__all__ = (
    "CollisionError",
)


class CollisionError(ValueError):
    """Exception thrown when a variable already exists"""

    message: str

    collisions: Collection[str]

    __match_args__ = __slots__ = ("message", "collisions")

    def __init__(self, message: str, collisions: Collection[str]) -> None:
        super().__init__(message, collisions)
        self.message = message
        self.collisions = collisions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, {self.collisions!r})"

    def __str__(self) -> str:
        collisions = ", ".join(self.collisions)
        return f"[collisions: {collisions}] {self.message}"
