#!/usr/bin/python3

"""Errors raised by Term operations"""

from __future__ import annotations
from collections.abc import Collection
from typing import TypeVar, Generic

__all__ = (
    "CollisionError",
)

V = TypeVar("V")


class CollisionError(ValueError, Generic[V]):
    """
    Exception thrown when a variable already exists,
    for example as a free variable.

    Type Variables:

        V: represents the type of variables

    :param message: message to be displayed
    :param collisions: variables which already exist
    """

    message: str

    collisions: Collection[V]

    __match_args__ = __slots__ = ("message", "collisions")

    def __init__(self, message: str, collisions: Collection[V]) -> None:
        super().__init__(message, collisions)
        self.message = message
        self.collisions = collisions

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__module__}.{self.__class__.__qualname__}"
            f"({self.message!r}, {self.collisions!r})"
        )

    def __str__(self) -> str:
        collisions = ", ".join(map(str, self.collisions))
        return f"[collisions: {collisions or 'none'}] {self.message}"
