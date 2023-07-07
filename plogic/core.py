"""Contains the Proposition class, its subclasses, and a related function."""

from abc import abstractmethod, ABC
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import overload, NoReturn, Union


class Proposition(ABC):
    """A `Proposition` object represents a logical proposition. This type
    serves as the base class for all proposition types in the `plogic` package.

    # Class Hierarchy

    The following is the class hierarchy for the `plogic` package:

    ```txt
    Proposition
        UnaryConnection
            Not
        BinaryConnection
            And
            Or
            Implies
            Iff
    ```

    The [`Not`](./#plogic.Not), [`And`](./#plogic.And), [`Or`](./#plogic.Or),
    [`Implies`](./#plogic.Implies), and [`Iff`](./#plogic.Iff) classes are all
    data classes, whose instances are composed of propositions.

    A `Not` object represents a logical negation and can be created using a
    single proposition: `Not(inner)`.

    `And`, `Or`, `Implies`, and `Iff` objects represent binary logical
    operations and can be created using two propositions. For example:
    `And(left, right)`.

    The [`UnaryConnection`](./#plogic.UnaryConnection) and
    [`BinaryConnection`](./#plogic.BinaryConnection) classes act as the
    abstract base classes for propositions constructed using unary and binary
    [logical connectives](https://en.wikipedia.org/wiki/Logical_connective).


    # Composing Compound Propositions

    This class provides five operations/methods to compose compound
    propositions:

    ## `~p`

    Returns [`Not(p)`](./#plogic.Not).

    ## `p & q`

    Returns [`And(p, q)`](./#plogic.And).

    ## `p | q`

    Returns [`Or(p, q)`](./#plogic.Or).

    ## `p.implies(q)`

    Returns [`Implies(p, q)`](./#plogic.Implies).

    ## `p.iff(q)`

    Returns [`Iff(p, q)`](./#plogic.Iff).

    Example:
        ```python
        p, q = props('P, Q')
        assert ~p == prop('~P')
        assert p & q == prop('P & Q')
        assert p | q == prop('P | Q')
        assert p.implies(q) == prop('P -> Q')
        assert p.iff(q) == prop('P <-> Q')
        ```

    # Accessing Component Propositions

    If a proposition is a compound proposition, you can use its fields to
    access the component propositions. **These fields are only present if the
    proposition is the correct type.**

    ## `p.inner`

    Inner operand of a unary operation.

    ## `p.left`, `p.right`

    Left and right operands of a binary operation.

    Example:

        ```python
        import plogic as pl

        s = pl.prop('~P')
        assert s.inner == pl.prop('P')

        t = pl.prop('P | Q')
        assert t.left == pl.prop('P')
        assert t.right == pl.prop('Q')
        ```

    # Interpreting: Assigning Truth Values

    To get the truth value of a proposition with respect to an interpretation,
    you can call the proposition with a mapping from atomic names to booleans.

    ## `p(mapping)`, `p(**kwargs)`

    Returns the truth value of the proposition given assignments from atomic
    names to truth values. Raises a `ValueError` if an atomic is interpreted
    but is not assigned a truth value.

    Example:
        ```python
        import plogic as pl

        u = pl.prop("p | q")

        # To interpret, call the proposition, assigning each atomic to a
        # boolean.
        assert u(p=True, q=True) is True
        assert u(p=True, q=False) is True
        assert u(p=False, q=True) is True
        assert u(p=True, q=False) is False

        # Map-like objects work too.
        assert u({'p': True, 'q': True}) is True
        assert u({'p': True, 'q': False}) is True
        assert u({'p': False, 'q': True}) is True
        assert u({'p': False, 'q': False}) is False
        ```

    Note: Note: Short Circuiting
        Interpreting a proposition uses "short circuiting" for efficiency.
        This means that the second operand will not be interpreted if the
        truth value of the first operand already determines the value of the
        connective.

        Short circuiting matters when not every atomic in the proposition is
        assigned a truth value. Normally, this would raise a `ValueError`, but
        if we never need to interpret the missing atomic, it may return a
        boolean instead.

        Example:

        ```python
        import plogic as pl

        u = pl.prop("p | q")
        assert u(p=True) is True  # No error because `q` was never interpreted
        ```

    # Comparing Propositions

    Propositions may be compared for structural equality using the `==` and
    `!=` operators. Inequality operators such as `>=`, `>`, `<`, and `<=`
    are not defined for this class.

    ## `p == q`

    Returns `True` if the two propositions are *structurally equal*, `False`
    otherwise.

    ## `p != q`

    Returns `True` if the two propositions are *NOT structurally equal*,
    `False` otherwise.

    Note:
        The `==` and `!=` operator **check for structural equivalence, not
        logical equivalence**.

    # Unsupported operations

    ## `bool(p)`

    Not supported. This raises a `TypeError`. See the
    [Interpreting](./#plogic.Proposition--interpreting-assigning-truth-values)
    section to learn how to assign truth values.

    """

    #
    # Methods for composing compound propositions
    #

    def __invert__(self, /) -> "Not":
        """Returns ``Not(p)``."""
        return Not(self)

    def __and__(self, other: "Proposition", /) -> "And":
        """Returns ``And(self, other)``."""
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
    # String Formatting
    #

    def __repr__(self) -> str:
        """Returns a string representation of this proposition."""
        return f"prop('{self!s}')"

    @abstractmethod
    def formal(self) -> str:
        """Returns the formal representation of this proposition.

        Returns:
            Formal representation of this proposition.
        """
        raise NotImplementedError(
            f"formal() is not implemented for '{self.__class__.__name__}'"
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


@dataclass(frozen=True, repr=False)
class Atomic(Proposition):
    name: str

    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        truth_value = interpretation.get(self.name)
        if truth_value is None:
            raise ValueError(f"Atomic '{self.name}' was left unassigned")
        return truth_value

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True, repr=False)
class UnaryConnection(Proposition):
    inner: Proposition


class Not(UnaryConnection):
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return not self.inner._interpret(interpretation)

    def __str__(self) -> str:
        return f"~{self.inner}"


@dataclass(frozen=True, repr=False)
class BinaryConnection(Proposition):
    left: Proposition
    right: Proposition


class And(BinaryConnection):
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return self.left._interpret(interpretation) and self.right._interpret(
            interpretation
        )

    def __str__(self) -> str:
        return f"({self.left} & {self.right})"


class Or(BinaryConnection):
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return self.left._interpret(interpretation) or self.right._interpret(
            interpretation
        )

    def __str__(self) -> str:
        return f"({self.left} | {self.right})"


class Implies(BinaryConnection):
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return not self.left._interpret(
            interpretation
        ) or self.right._interpret(interpretation)

    def __str__(self) -> str:
        return f"({self.left} -> {self.right})"


class Iff(BinaryConnection):
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        return self.left._interpret(interpretation) == self.right._interpret(
            interpretation
        )

    def __str__(self) -> str:
        return f"({self.left} <-> {self.right})"


@overload
def atomics(names_sep_by_spaces: str, /) -> tuple[Atomic, ...]:
    ...


@overload
def atomics(name_iterable: Iterable[str], /) -> tuple[Atomic, ...]:
    ...


def atomics(arg: Union[str, Iterable[str]], /) -> tuple[Atomic, ...]:
    if isinstance(arg, str):
        arg = arg.split()
    return tuple(Atomic(name) for name in arg)
