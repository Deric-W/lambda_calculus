#!/usr/bin/python3

"""Implementation of the Lambda calculus"""

from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Set, Sequence
from dataclasses import dataclass
from typing import TypeVar
from .errors import CollisionError

__version__ = "0.0.1"
__author__  = "Eric Niklas Wolf"
__email__   = "eric_niklas.wolf@mailbox.tu-dresden.de"
__all__ = (
    "Term",
    "Variable",
    "Abstraction",
    "Application",
    "errors"
)

T = TypeVar("T")


class Term(ABC):
    """ABC for Lambda terms"""

    __slots__ = ("__weakref__",)

    @abstractmethod
    def free_variables(self) -> Set[str]:
        """return the free variables of this Term"""
        raise NotImplementedError()

    @abstractmethod
    def bound_variables(self) -> Set[str]:
        """return the bound variables of this Term"""
        raise NotImplementedError()

    @abstractmethod
    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        raise NotImplementedError()

    @abstractmethod
    def replace(self, variable: str, value: Term) -> Term:
        """replace a free variable with a Term"""
        raise NotImplementedError()

    @abstractmethod
    def rename(self: T, variable: str, new: str) -> T:
        """rename a variable, even if this would change the meaning of the Term"""
        raise NotImplementedError()

    def is_combinator(self) -> bool:
        """return if this Term has no free variables"""
        return not self.free_variables()


@dataclass(unsafe_hash=True, slots=True)
class Variable(Term):
    """Term consiting of a Variable"""

    name: str

    @classmethod
    def with_valid_name(cls, name: str) -> Variable:
        """create an instance with a valid name or raise ValueError"""
        for character in name:
            if character in "().λ" or character.isspace():
                raise ValueError(f"invalid character: '{character}'")
        return cls(name)

    def __str__(self) -> str:
        return self.name

    def free_variables(self) -> Set[str]:
        """return the free variables of this Term"""
        return {self.name}

    def bound_variables(self) -> Set[str]:
        """return the bound variables of this Term"""
        return set()

    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        return True

    def replace(self, variable: str, value: Term) -> Term:
        """replace a free variable with a Term, may change the meaning of the value"""
        if variable == self.name:
            return value
        return self

    def rename(self, variable: str, new: str) -> Variable:
        """rename a variable, may change the meaning of the Term"""
        if variable == self.name:
            return Variable(new)
        return self


@dataclass(unsafe_hash=True, slots=True)
class Abstraction(Term):
    """Term consisting of a lambda abstraction"""

    bound: str

    body: Term

    @classmethod
    def curried(cls, variables: Sequence[str], body: Term) -> Abstraction:
        """create an Abstraction binding multiple variables"""
        match variables:
            case [*variables, inner]:
                term = cls(inner, body)
                for variable in reversed(variables):
                    term = cls(variable, term)
                return term
            case _:
                raise ValueError("no variables to bind")

    def __str__(self) -> str:
        return f"(λ{self.bound}.{self.body})"

    def free_variables(self) -> Set[str]:
        """return the free variables of this Term"""
        return self.body.free_variables() - {self.bound}

    def bound_variables(self) -> Set[str]:
        """return the bound variables of this Term"""
        return self.body.bound_variables() | {self.bound}

    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        return self.body.is_beta_normal_form()

    def replace(self, variable: str, value: Term) -> Abstraction:
        """replace a free variable with a Term"""
        if variable == self.bound:
            return self
        return Abstraction(self.bound, self.body.replace(variable, value))

    def rename(self, variable: str, new: str) -> Abstraction:
        """rename a variable, even if this would change the meaning of the Term"""
        if new == self.bound:
            return Abstraction(new, self.body.rename(variable, new))
        return Abstraction(self.bound, self.body.rename(variable, new))

    def alpha_conversion(self, new: str) -> Abstraction:
        """rename the bound variable"""
        if new == self.bound:
            return self
        elif new not in self.body.bound_variables() and new not in self.body.free_variables():
            return Abstraction(
                new,
                self.body.rename(self.bound, new)
            )
        raise CollisionError("variable already exists in body", (new,))


@dataclass(unsafe_hash=True, slots=True)
class Application(Term):
    """Term consisting of an application"""

    abstraction: Term

    argument: Term

    @classmethod
    def with_arguments(cls, abstraction: Term, arguments: Sequence[Term]) -> Application:
        """create an Application applying the abstraction to multiple arguments"""
        match arguments:
            case [first, *rest]:
                term = cls(abstraction, first)
                for argument in rest:
                    term = cls(term, argument)
                return term
            case _:
                raise ValueError("no arguments to apply abstraction to")

    def __str__(self) -> str:
        return f"({self.abstraction} {self.argument})"

    def free_variables(self) -> Set[str]:
        """return the free variables of this Term"""
        return self.abstraction.free_variables() | self.argument.free_variables()

    def bound_variables(self) -> Set[str]:
        """return the bound variables of this Term"""
        return self.abstraction.bound_variables() | self.argument.bound_variables()

    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        return not isinstance(self.abstraction, Abstraction) \
            and self.abstraction.is_beta_normal_form() \
            and self.argument.is_beta_normal_form()

    def replace(self, variable: str, value: Term) -> Application:
        """replace a free variable with a Term"""
        return Application(
            self.abstraction.replace(variable, value),
            self.argument.replace(variable, value)
        )

    def rename(self, variable: str, new: str) -> Application:
        """rename a variable, even if this would change the meaning of the Term"""
        return Application(
            self.abstraction.rename(variable, new),
            self.argument.rename(variable, new)
        )

    def beta_reduction(self) -> Term:
        """remove an abstraction"""
        match self.abstraction:
            case Abstraction(bound, body):
                collisions = body.bound_variables() & self.argument.free_variables()
                if collisions:
                    raise CollisionError("free variables in argument are bound in abstraction", collisions)
                return body.replace(bound, self.argument)
            case _:
                raise ValueError("can not perform reduction without known Abstraction")
