#!/usr/bin/python3

"""Lambda Terms"""

from __future__ import annotations
from abc import abstractmethod
from collections.abc import Sequence, Set, Iterable, Iterator
from dataclasses import dataclass
from typing import TypeVar
from .. import visitors
from ..errors import CollisionError
from ..visitors import substitution, walking

__all__ = (
    "Term",
    "Variable",
    "Abstraction",
    "Application",
    "arithmetic",
    "logic",
    "pairs"
)

T = TypeVar("T")
V = TypeVar("V")


class Term(Iterable["Term[V]"]):
    """ABC for Lambda terms"""

    __slots__ = ("__weakref__",)

    def __iter__(self) -> Iterator[Term[V]]:
        return self.accept(walking.DepthFirstVisitor())

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
    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """accept a visitor by calling his corresponding method"""
        raise NotImplementedError()

    def abstract(self, *variables: V) -> Abstraction[V]:
        """create an Abstraction binding multiple variables"""
        return Abstraction.curried(variables, self)

    def apply_to(self, *arguments: Term[V]) -> Application[V]:
        """create an Application applying self to multiple arguments"""
        return Application.with_arguments(self, arguments)

    def substitute(self, variable: V, value: Term[V]) -> Term[V]:
        """substitute a free variable with a Term, possibly raising a CollisionError"""
        return self.accept(substitution.SubstitutingVisitor(variable, value))

    def is_combinator(self) -> bool:
        """return if this Term has no free variables"""
        return not self.free_variables()


@dataclass(unsafe_hash=True, slots=True)
class Variable(Term[V]):
    """Term consisting of a Variable"""

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

    def alpha_conversion(self, new: V) -> Abstraction[V]:
        """rename the bound variable"""
        if new == self.bound:
            return self
        elif new not in self.body.free_variables():
            return Abstraction(
                new,
                self.body.substitute(self.bound, Variable(new))
            )
        raise CollisionError("new variable would bind free variable in body", (new,))

    def eta_reduction(self) -> Term[V]:   # type: ignore[return]
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

    def replace(self, *, bound: V | None = None, body: Term[V] | None = None) -> Abstraction[V]:
        """return a copy with specific attributes replaced"""
        return Abstraction(
            self.bound if bound is None else bound,
            self.body if body is None else body
        )


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

    def is_redex(self) -> bool:
        """return if this term can be reduced"""
        return isinstance(self.abstraction, Abstraction)

    def is_beta_normal_form(self) -> bool:
        """return if this Term is in beta-normal form"""
        return not self.is_redex() \
            and self.abstraction.is_beta_normal_form() \
            and self.argument.is_beta_normal_form()

    def beta_reduction(self) -> Term[V]:
        """remove an abstraction"""
        match self.abstraction:
            case Abstraction(bound, body):
                return body.substitute(bound, self.argument)
            case _:
                raise ValueError("can not perform reduction without known Abstraction")

    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """accept a visitor by calling his corresponding method"""
        return visitor.visit_application(self)

    def replace(self, *, abstraction: Term[V] | None = None, argument: Term[V] | None = None) -> Application[V]:
        """return a copy with specific attributes replaced"""
        return Application(
            self.abstraction if abstraction is None else abstraction,
            self.argument if argument is None else argument
        )
