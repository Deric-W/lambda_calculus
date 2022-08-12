#!/usr/bin/python3

"""Lambda Term implementations"""

from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Set, Sequence
from dataclasses import dataclass
from typing import TypeVar, Generic
from . import visitors
from .errors import CollisionError

__all__ = (
    "Term",
    "Variable",
    "Abstraction",
    "Application"
)

T = TypeVar("T")
V = TypeVar("V")


class Term(ABC, Generic[V]):
    """ABC for Lambda terms"""

    __slots__ = ("__weakref__",)

    @abstractmethod
    def free_variables(self) -> Set[V]:
        """return the free variables of this Term"""
        raise NotImplementedError()

    @abstractmethod
    def bound_variables(self) -> Set[V]:
        """return the bound variables of this Term"""
        raise NotImplementedError()

    @abstractmethod
    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        raise NotImplementedError()

    @abstractmethod
    def replace(self, variable: V, value: Term[V]) -> Term[V]:
        """replace a free variable with a Term"""
        raise NotImplementedError()

    @abstractmethod
    def rename(self: T, variable: V, new: V) -> T:
        """rename a variable, even if this would change the meaning of the Term"""
        raise NotImplementedError()

    @abstractmethod
    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """accept a visitor by calling his corresponding method"""
        raise NotImplementedError()

    def is_combinator(self) -> bool:
        """return if this Term has no free variables"""
        return not self.free_variables()


@dataclass(unsafe_hash=True, slots=True)
class Variable(Term[V]):
    """Term consiting of a Variable"""

    name: V

    @classmethod
    def with_valid_name(cls, name: V) -> Variable[V]:
        """create an instance with a valid name or raise ValueError"""
        string = str(name)
        if not string:
            raise ValueError("empty string representation")
        for character in string:
            if character in "().λ" or character.isspace():
                raise ValueError(f"invalid character: '{character}'")
        return cls(name)

    def __str__(self) -> str:
        return str(self.name)

    def free_variables(self) -> Set[V]:
        """return the free variables of this Term"""
        return {self.name}

    def bound_variables(self) -> Set[V]:
        """return the bound variables of this Term"""
        return set()

    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        return True

    def replace(self, variable: V, value: Term[V]) -> Term[V]:
        """replace a free variable with a Term, may change the meaning of the value"""
        if variable == self.name:
            return value
        return self

    def rename(self, variable: V, new: V) -> Variable[V]:
        """rename a variable, may change the meaning of the Term"""
        if variable == self.name:
            return Variable(new)
        return self

    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """accept a visitor by calling his corresponding method"""
        return visitor.visit_variable(self)


@dataclass(unsafe_hash=True, slots=True)
class Abstraction(Term[V]):
    """Term consisting of a lambda abstraction"""

    bound: V

    body: Term[V]

    @classmethod
    def curried(cls, variables: Sequence[V], body: Term[V]) -> Abstraction[V]:
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

    def free_variables(self) -> Set[V]:
        """return the free variables of this Term"""
        return self.body.free_variables() - {self.bound}

    def bound_variables(self) -> Set[V]:
        """return the bound variables of this Term"""
        return self.body.bound_variables() | {self.bound}

    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        return self.body.is_beta_normal_form()

    def replace(self, variable: V, value: Term[V]) -> Abstraction[V]:
        """replace a free variable with a Term"""
        if variable == self.bound:
            return self
        return Abstraction(self.bound, self.body.replace(variable, value))

    def rename(self, variable: V, new: V) -> Abstraction[V]:
        """rename a variable, even if this would change the meaning of the Term"""
        if new == self.bound:
            return Abstraction(new, self.body.rename(variable, new))
        return Abstraction(self.bound, self.body.rename(variable, new))

    def alpha_conversion(self, new: V) -> Abstraction[V]:
        """rename the bound variable"""
        if new == self.bound:
            return self
        elif new not in self.body.bound_variables() and new not in self.body.free_variables():
            return Abstraction(
                new,
                self.body.rename(self.bound, new)
            )
        raise CollisionError("variable already exists in body", (new,))

    def eta_conversion(self) -> Term[V]:   # type: ignore[return]
        """remove a useless abstraction"""
        match self.body:
            case Application(f, Variable(x)) if x == self.bound and x not in f.free_variables():
                return f
            case _:
                # mypy detects missing returns
                # because of https://github.com/python/mypy/issues/12534
                raise ValueError("abstraction is not useless")

    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """accept a visitor by calling his corresponding method"""
        return visitor.visit_abstraction(self)


@dataclass(unsafe_hash=True, slots=True)
class Application(Term[V]):
    """Term consisting of an application"""

    abstraction: Term[V]

    argument: Term[V]

    @classmethod
    def with_arguments(cls, abstraction: Term[V], arguments: Sequence[Term[V]]) -> Application[V]:
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

    def free_variables(self) -> Set[V]:
        """return the free variables of this Term"""
        return self.abstraction.free_variables() | self.argument.free_variables()

    def bound_variables(self) -> Set[V]:
        """return the bound variables of this Term"""
        return self.abstraction.bound_variables() | self.argument.bound_variables()

    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        return not isinstance(self.abstraction, Abstraction) \
            and self.abstraction.is_beta_normal_form() \
            and self.argument.is_beta_normal_form()

    def replace(self, variable: V, value: Term[V]) -> Application[V]:
        """replace a free variable with a Term"""
        return Application(
            self.abstraction.replace(variable, value),
            self.argument.replace(variable, value)
        )

    def rename(self, variable: V, new: V) -> Application[V]:
        """rename a variable, even if this would change the meaning of the Term"""
        return Application(
            self.abstraction.rename(variable, new),
            self.argument.rename(variable, new)
        )

    def beta_reduction(self) -> Term[V]:
        """remove an abstraction"""
        match self.abstraction:
            case Abstraction(bound, body):
                collisions = body.bound_variables() & self.argument.free_variables()
                if collisions:
                    raise CollisionError("free variables in argument are bound in abstraction", collisions)
                return body.replace(bound, self.argument)
            case _:
                raise ValueError("can not perform reduction without known Abstraction")

    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """accept a visitor by calling his corresponding method"""
        return visitor.visit_application(self)
