"""Contains the Proposition class, its subclasses, and a related function."""

from abc import ABC
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import overload, NoReturn, Union


class Proposition(ABC):
    """Represents a proposition in logic.

    This is an abstract base class for all proposition classes.
    """

    #
    # Functions for composing compound propositions
    #

    def __invert__(self, /) -> "Not":
        return Not(self)

    def __and__(self, other: "Proposition", /) -> "And":
        if isinstance(other, Proposition):
            return And(self, other)
        return NotImplemented

    def __or__(self, other: "Proposition", /) -> "Or":
        if isinstance(other, Proposition):
            return Or(self, other)
        return NotImplemented

    def implies(self, other: "Proposition", /) -> "Implies":
        return Implies(self, other)

    def iff(self, other: "Proposition", /) -> "Iff":
        return Iff(self, other)

    #
    # Function for the proposition's truth value under an interpretation
    #

    @overload
    def __call__(self, vals: Mapping[str, bool], /) -> bool:
        ...

    @overload
    def __call__(self, /, **vals: bool) -> bool:
        ...

    def __call__(self, mapping=None, /, **kwargs) -> bool:
        pass  # TODO implement

    #
    # Miscellaneous special functions
    #

    def __bool__(self) -> NoReturn:
        pass  # TODO implement

    def __str__(self) -> str:
        pass  # TODO implement


# TODO documentation and full implementation of the subclasses


@dataclass(frozen=True)
class Atomic:
    name: str


@dataclass(frozen=True)
class UnaryConnection(Proposition):
    inner: Proposition


class Not(UnaryConnection):
    pass


@dataclass(frozen=True)
class BinaryConnection(Proposition):
    pass


@dataclass(frozen=True)
class And(BinaryConnection):
    left: Proposition
    right: Proposition


@dataclass(frozen=True)
class Or(BinaryConnection):
    left: Proposition
    right: Proposition


@dataclass(frozen=True)
class Implies(BinaryConnection):
    left: Proposition
    right: Proposition


@dataclass(frozen=True)
class Iff(BinaryConnection):
    left: Proposition
    right: Proposition


@overload
def atomics(names_sep_by_spaces: str, /) -> tuple[Atomic, ...]:
    ...


@overload
def atomics(name_iter: Iterable[str], /) -> tuple[Atomic, ...]:
    ...


def atomics(arg, /):
    pass  # TODO implement
