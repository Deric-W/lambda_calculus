#!/usr/bin/python3

"""Lambda Terms"""

from __future__ import annotations
from abc import abstractmethod
from collections.abc import Sequence, Set, Iterable, Iterator
from dataclasses import dataclass
from typing import TypeVar
from .. import visitors
from ..errors import CollisionError
from ..visitors import walking
from ..visitors.substitution import checked

__all__ = (
    "Term",
    "Variable",
    "Abstraction",
    "Application",
    "arithmetic",
    "logic",
    "pairs",
    "combinators"
)

T = TypeVar("T")
V = TypeVar("V")


class Term(Iterable["Term[V]"]):
    """
    ABC for Lambda terms.

    Type Variables:

        V: represents the type of variables used in terms
    """

    __slots__ = ("__weakref__",)

    def __iter__(self) -> Iterator[Term[V]]:
        """
        :return: Iterator over all subterms
        """
        return self.accept(walking.DepthFirstVisitor())

    @abstractmethod
    def __str__(self) -> str:
        """
        Create a string representation.

        :return: lambda term string
        """
        raise NotImplementedError()

    @abstractmethod
    def free_variables(self) -> Set[V]:
        """
        Calculate the free variables of this Term.

        :return: variables not bound by an abstraction
        """
        raise NotImplementedError()

    @abstractmethod
    def bound_variables(self) -> Set[V]:
        """
        Calculate the bound variables of this Term.

        :return: variables bound by an abstraction
        """
        raise NotImplementedError()

    @abstractmethod
    def is_beta_normal_form(self) -> bool:
        """
        Check if this Term is in beta-normal form.

        :return: if no beta reductions can be performed
        """
        raise NotImplementedError()

    @abstractmethod
    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """
        Accept a visitor by calling his corresponding method.

        :param visitor: Visitor to accept
        :return: value returned by the visitors corresponding method
        """
        raise NotImplementedError()

    def abstract(self, *variables: V) -> Abstraction[V]:
        """
        Create an Abstraction binding multiple variables.

        :param variables: Variables to bind, from first to last
        :return: requested Abstraction term
        """
        return Abstraction.curried(variables, self)

    def apply_to(self, *arguments: Term[V]) -> Application[V]:
        """
        Create an Application applying self to multiple arguments.

        :param arguments: arguments to apply to, from first to last
        :return: requested Application term
        """
        return Application.with_arguments(self, arguments)

    def substitute(self, variable: V, value: Term[V]) -> Term[V]:
        """
        Substitute a free variable with a Term.

        :param variable: Variable to substitute
        :param value: Value to be substituted
        :raise errors.CollisionError: If substitution would bind free variables
        :return: new term
        """
        return self.accept(checked.CheckedSubstitution.from_substitution(variable, value))

    def is_combinator(self) -> bool:
        """
        Check if this Term has no free variables.

        :return: If there are no free variables
        """
        return not self.free_variables()


@dataclass(unsafe_hash=True, slots=True)
class Variable(Term[V]):
    """
    Term consisting of a Variable

    :param name: Name of the Variable
    """

    name: V

    @classmethod
    def with_valid_name(cls, name: V) -> Variable[V]:
        """
        Create an instance with a valid name.

        :param name: Name of the Variable
        :raise ValueError: If the name would conflict with string representations
        :return: requested Variable term
        """
        string = str(name)
        if not string:
            raise ValueError("empty string representation")
        for character in string:
            if character in "().λ" or character.isspace():
                raise ValueError(f"invalid character: '{character}'")
        return cls(name)

    def __str__(self) -> str:
        """
        Create a string representation.

        :return: variable name
        """
        return str(self.name)

    def free_variables(self) -> Set[V]:
        """
        Calculate the free variables of this Term.

        :return: variables not bound by an abstraction
        """
        return {self.name}

    def bound_variables(self) -> Set[V]:
        """
        Calculate the bound variables of this Term.

        :return: variables bound by an abstraction
        """
        return set()

    def is_beta_normal_form(self) -> bool:
        """
        Check if this Term is in beta-normal form.

        :return: if no beta reductions can be performed
        """
        return True

    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """
        Accept a visitor by calling visitors.Visitor.visit_variable.

        :param visitor: Visitor to accept
        :return: value returned by visitors.Visitor.visit_variable
        """
        return visitor.visit_variable(self)


@dataclass(unsafe_hash=True, slots=True)
class Abstraction(Term[V]):
    """
    Term consisting of a lambda abstraction.

    :param bound: variable to be bound by this abstraction
    :param body: term to be abstracted
    """

    bound: V

    body: Term[V]

    @classmethod
    def curried(cls, variables: Sequence[V], body: Term[V]) -> Abstraction[V]:
        """
        Create an Abstraction binding multiple variables.

        :param variables: variables to be bound, from first to last
        :param body: term to be abstracted
        :raise ValueError: If no variables are passed
        :return: requested Abstraction term
        """
        match variables:
            case [*variables, inner]:
                term = cls(inner, body)
                for variable in reversed(variables):
                    term = cls(variable, term)
                return term
            case _:
                raise ValueError("no variables to bind")

    def __str__(self) -> str:
        """
        Create a string representation.

        :return: (λ{bound}.{body})
        """
        return f"(λ{self.bound}.{self.body})"

    def free_variables(self) -> Set[V]:
        """
        Calculate the free variables of this Term.

        :return: variables not bound by an abstraction
        """
        return self.body.free_variables() - {self.bound}

    def bound_variables(self) -> Set[V]:
        """
        Calculate the free variables of this Term.

        :return: variables not bound by an abstraction
        """
        return self.body.bound_variables() | {self.bound}

    def is_beta_normal_form(self) -> bool:
        """
        Check if this Term is in beta-normal form.

        :return: if no beta reductions can be performed
        """
        return self.body.is_beta_normal_form()

    def alpha_conversion(self, new: V) -> Abstraction[V]:
        """
        Rename the bound variable

        :param new: new variable to bind
        :raise errors.CollisionError: If the new variable is a free variable
        :return: new term
        """
        if new == self.bound:
            return self
        elif new not in self.body.free_variables():
            return Abstraction(
                new,
                self.body.substitute(self.bound, Variable(new))
            )
        raise CollisionError("new variable would bind free variable in body", (new,))

    def eta_reduction(self) -> Term[V]:   # type: ignore[return]
        """
        Remove a useless abstraction.

        :raise ValueError: If abstraction is not useless
        :return: new term
        """
        match self.body:
            case Application(f, Variable(x)) if x == self.bound and x not in f.free_variables():
                return f
            case _:
                # mypy detects missing returns
                # because of https://github.com/python/mypy/issues/12534
                raise ValueError("abstraction is not useless")

    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """
        Accept a visitor by calling visitors.Visitor.visit_abstraction.

        :param visitor: Visitor to accept
        :return: value returned by visitors.Visitor.visit_abstraction
        """
        return visitor.visit_abstraction(self)

    def replace(self, *, bound: V | None = None, body: Term[V] | None = None) -> Abstraction[V]:
        """
        Return a copy with specific attributes replaced.

        :param bound: new value for bound variable, defaults to current
        :param body: new value for body, defaults to current
        :return: new term
        """
        return Abstraction(
            self.bound if bound is None else bound,
            self.body if body is None else body
        )


@dataclass(unsafe_hash=True, slots=True)
class Application(Term[V]):
    """
    Term consisting of an application.

    :param abstraction: abstraction to be applied
    :param argument: argument which to apply the abstraction to
    """

    abstraction: Term[V]

    argument: Term[V]

    @classmethod
    def with_arguments(cls, abstraction: Term[V], arguments: Sequence[Term[V]]) -> Application[V]:
        """
        Create an Application applying the abstraction to multiple arguments.

        :param abstraction: abstraction to be applied
        :param arguments: arguments which to apply the abstraction to, from first to last
        :raise ValueError: If no arguments are passed
        :return: requested Application term
        """
        match arguments:
            case [first, *rest]:
                term = cls(abstraction, first)
                for argument in rest:
                    term = cls(term, argument)
                return term
            case _:
                raise ValueError("no arguments to apply abstraction to")

    def __str__(self) -> str:
        """
        Create a string representation.

        :return: ({abstraction} {argument})
        """
        return f"({self.abstraction} {self.argument})"

    def free_variables(self) -> Set[V]:
        """
        Calculate the free variables of this Term.

        :return: variables not bound by an abstraction
        """
        return self.abstraction.free_variables() | self.argument.free_variables()

    def bound_variables(self) -> Set[V]:
        """
        Calculate the free variables of this Term.

        :return: variables not bound by an abstraction
        """
        return self.abstraction.bound_variables() | self.argument.bound_variables()

    def is_redex(self) -> bool:
        """
        Check if this term can be reduced.

        :return: If a beta reduction can be performed
        """
        return isinstance(self.abstraction, Abstraction)

    def is_beta_normal_form(self) -> bool:
        """
        Check if this Term is in beta-normal form.

        :return: if no beta reductions can be performed
        """
        return not self.is_redex() \
            and self.abstraction.is_beta_normal_form() \
            and self.argument.is_beta_normal_form()

    def beta_reduction(self) -> Term[V]:
        """
        Remove the abstraction.

        :raise ValueError: If this term can not be reduced
        :return: new term
        """
        match self.abstraction:
            case Abstraction(bound, body):
                return body.substitute(bound, self.argument)
            case _:
                raise ValueError("can not perform reduction without known Abstraction")

    def accept(self, visitor: visitors.Visitor[T, V]) -> T:
        """
        Accept a visitor by calling visitors.Visitor.visit_application.

        :param visitor: Visitor to accept
        :return: value returned by visitors.Visitor.visit_application
        """
        return visitor.visit_application(self)

    def replace(self, *, abstraction: Term[V] | None = None, argument: Term[V] | None = None) -> Application[V]:
        """
        Return a copy with specific attributes replaced.

        :param abstraction: abstraction to be applied, defaults to current
        :param argument: argument which to apply the abstraction to, defaults to current
        :return: new term
        """
        return Application(
            self.abstraction if abstraction is None else abstraction,
            self.argument if argument is None else argument
        )
