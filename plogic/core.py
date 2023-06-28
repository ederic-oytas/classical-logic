"""Contains the Proposition class, its subclasses, and a related function."""

from abc import abstractmethod, ABC
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import overload, NoReturn


class Proposition(ABC):
    """Represents a proposition in logic.

    This is an abstract base class for all proposition classes.
    """

    #
    # Methods for composing compound propositions
    #

    def __invert__(self, /) -> "Not":
        """Returns ``Not(p)``."""
        return Not(self)

    def __and__(self, other: "Proposition", /) -> "And":
        """Returns ``And(p, q)``."""
        if isinstance(other, Proposition):
            return And(self, other)
        return NotImplemented

    def __or__(self, other: "Proposition", /) -> "Or":
        """Returns ``Or(p, q)``."""
        if isinstance(other, Proposition):
            return Or(self, other)
        return NotImplemented

    def implies(self, other: "Proposition", /) -> "Implies":
        """Returns ``Implies(p, q)``."""
        return Implies(self, other)

    def iff(self, other: "Proposition", /) -> "Iff":
        """Returns ``Iff(p, q)``,"""
        return Iff(self, other)

    #
    # Method for the proposition's truth value under an interpretation
    #

    @overload
    def __call__(self, vals: Mapping[str, bool], /) -> bool:
        """Returns the truth value of this proposition under the given
        assignment of atomic names to truth values, otherwise known as
        interpreting.

        Note: This may use "short circuiting." If the truth value of a left
            operand in a two-place connection determines the truth value of the
            connection to be true or false regardless of the truth value of the
            second operand, then the second operand is not interpreted. This
            matters in the case of missing atomics. If the second operand
            happens to contain an atomic which isn't included in the given
            truth value mapping, then it wouldn't raise a ValueError.

        Args:
            vals: Mapping from atomic names to truth values.

        Returns:
            Truth value of this proposition under the given mapping.

        Raises:
            ValueError: At least one atomic was left unassigned in the mapping.
        """

    @overload
    def __call__(self, /, **vals: bool) -> bool:
        """Returns the truth value of this proposition under the given
        assignment of atomic names to truth values, otherwise known as
        interpreting.

        Note: This may use "short circuiting." If the truth value of a left
            operand in a two-place connection determines the truth value of the
            connection to be true or false regardless of the truth value of the
            second operand, then the second operand is not interpreted. This
            matters in the case of missing atomics. If the second operand
            happens to contain an atomic which isn't included in the given
            truth value mapping, then it wouldn't raise a ValueError.

        Args:
            vals: Assignments of atomic names to truth values.

        Returns:
            Truth value of this proposition under the given assignments.

        Raises:
            ValueError: At least one atomic was left unassigned.
        """

    def __call__(self, mapping=None, /, **kwargs) -> bool:
        if mapping is None:
            return self._interpret(kwargs)
        return self._interpret(mapping)

    @abstractmethod
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        """Returns the truth value of this proposition under the given mapping
        from atomic names to truth values.

        This is an abstract internal method which is delegated to by __call__.
        """
        raise NotImplementedError(
            f"'_interpret' is not implemented for '{self.__class__.__name__}'"
        )

    #
    # Miscellaneous special methods
    #

    def __bool__(self) -> NoReturn:
        """Raises TypeError. ``bool(p)`` is not supported because the truth
        value of an `Proposition` is ambiguous."""
        raise TypeError(
            "The truth value of a Proposition is ambiguous. Consider using "
            "interpretation through p(**vals)"
        )


# TODO documentation and full implementation of the subclasses


@dataclass(frozen=True)
class Atomic(Proposition):
    name: str

    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        truth_value = interpretation.get(self.name)
        if truth_value is None:
            raise ValueError(f"Atomic '{self.name}' was left unassigned")
        return truth_value

    def __str__(self) -> str:
        return ""  # TODO implement


@dataclass(frozen=True)
class UnaryConnection(Proposition):
    inner: Proposition


class Not(UnaryConnection):
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return not self.inner._interpret(interpretation)

    def __str__(self) -> str:
        return ""  # TODO implement


@dataclass(frozen=True)
class BinaryConnection(Proposition):
    pass


@dataclass(frozen=True)
class And(BinaryConnection):
    left: Proposition
    right: Proposition

    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return self.left._interpret(interpretation) and self.right._interpret(
            interpretation
        )

    def __str__(self) -> str:
        return ""  # TODO implement


@dataclass(frozen=True)
class Or(BinaryConnection):
    left: Proposition
    right: Proposition

    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return self.left._interpret(interpretation) or self.right._interpret(
            interpretation
        )

    def __str__(self) -> str:
        return ""  # TODO implement


@dataclass(frozen=True)
class Implies(BinaryConnection):
    left: Proposition
    right: Proposition

    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return not self.left._interpret(
            interpretation
        ) or self.right._interpret(interpretation)

    def __str__(self) -> str:
        return ""  # TODO implement


@dataclass(frozen=True)
class Iff(BinaryConnection):
    left: Proposition
    right: Proposition

    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return self.left._interpret(interpretation) == self.right._interpret(
            interpretation
        )

    def __str__(self) -> str:
        return ""  # TODO implement


@overload
def atomics(names_sep_by_spaces: str, /) -> tuple[Atomic, ...]:
    ...


@overload
def atomics(name_iterable: Iterable[str], /) -> tuple[Atomic, ...]:
    ...


def atomics(arg, /):
    return ()  # TODO implement
