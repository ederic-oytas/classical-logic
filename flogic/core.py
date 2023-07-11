"""Contains the Proposition class, its subclasses, and a related function.


Class Hierarchy:

```
Proposition
    Predicate
    _Operation1
        Not
    _Operation2
        And
        Or
        Implies
        Iff
```
"""

from abc import abstractmethod, ABC
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
import re
from typing import overload, NoReturn, Union


class Proposition(ABC):
    """Represents a logical proposition. This type serves as the base class
    for all proposition types in the `flogic` package.

    # Operation Summary

    The following table summarizes the special operations on this class:

    Operation     | Description
    --------------|---------------------------------------------------
    `p[i]`        | Gets the component of `p` at index `i`.
    `iter(p)`     | Returns an iterator over the components of `p`.
    `~p`          | Returns [`Not(p)`][flogic.Not].
    `p & q`       | Returns [`And(p, q)`][flogic.And].
    `p | q`       | Returns [`Or(p, q)`][flogic.Or].
    `p(mapping)`  | [Interprets][1] `p`.
    `p(**kwargs)` | [Interprets][1] `p`.
    `p == q`      | Checks if `p` and `q` are structurally equal.
    `p != q`      | Checks if `p` and `q` are not structurally equal.
    `hash(p)`     | Returns the hash value of `p`.
    `str(p)`      | See [string formatting](). TODO link formatting section
    `repr(p)`     | See [string formatting](). TODO link formatting section

    **Note:** `bool(p)` is not supported as the truth value of a proposition is
    ambiguous.

    [1]: ./#flogic.Proposition--interpreting-assigning-truth-values
    """

    """

    OLD DOCUMENTATION; MAYBE MOVE TO USER GUIDE

    # Class Hierarchy

    The following is the class hierarchy for the `flogic` package:

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

    The [`Not`](./#flogic.Not), [`And`](./#flogic.And), [`Or`](./#flogic.Or),
    [`Implies`](./#flogic.Implies), and [`Iff`](./#flogic.Iff) classes are all
    data classes, whose instances are composed of propositions.

    A `Not` object represents a logical negation and can be created using a
    single proposition: `Not(inner)`.

    `And`, `Or`, `Implies`, and `Iff` objects represent binary logical
    operations and can be created using two propositions. For example:
    `And(left, right)`.

    The [`UnaryConnection`](./#flogic.UnaryConnection) and
    [`BinaryConnection`](./#flogic.BinaryConnection) classes act as the
    abstract base classes for propositions constructed using unary and binary
    [logical connectives](https://en.wikipedia.org/wiki/Logical_connective).


    # Composing Compound Propositions

    This class provides five operations/methods to compose compound
    propositions:

    ## `~p`

    Returns [`Not(p)`](./#flogic.Not).

    ## `p & q`

    Returns [`And(p, q)`](./#flogic.And).

    ## `p | q`

    Returns [`Or(p, q)`](./#flogic.Or).

    ## `p.implies(q)`

    Returns [`Implies(p, q)`](./#flogic.Implies).

    ## `p.iff(q)`

    Returns [`Iff(p, q)`](./#flogic.Iff).

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
        import flogic as pl

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
        import flogic as pl

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
        import flogic as pl

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
    [Interpreting](./#flogic.Proposition--interpreting-assigning-truth-values)
    section to learn how to assign truth values.

    """

    #
    # Accessing Methods
    #

    @abstractmethod
    def __getitem__(self, index: int, /) -> "Proposition":
        """Returns the immediate component proposition indicated by the
        index."""
        raise NotImplementedError(
            f"__getitem__ is not implemented for '{self.__class__.__name__}'"
        )

    @abstractmethod
    def __iter__(self, /) -> Iterator["Proposition"]:
        """Iterates over this proposition's immediate component
        propositions."""
        raise NotImplementedError(
            f"__iter__ is not implemented for '{self.__class__.__name__}'"
        )

    #
    # Degree method
    #

    @abstractmethod
    def degree(self) -> int:
        """Returns the number of components this proposition contains.

        For example, a negation (`~P`) has a degree of `1` because it's a
        unary (two-place) operation, which takes one operand.

        A conjunction (`P & Q`) and a disjunction (`P | Q`) both have degrees
        of `2`, because they are both binary (two-place) operations.

        A predicate (`P`) has a degree of `0`, since it doesn't contain any
        components.

        Example:
            ```python
            import flogic as fl


            # Degree of a predicate is 0
            assert fl.prop('P').degree() == 0

            # Degree of a negation is 1
            assert fl.prop('~P').degree() == 1

            # The outermost connective determines the degree
            assert fl.prop('~~~P').degree() == 1
            assert fl.prop('~(~~P)').degree() == 1

            # Degree of a binary (two-place) operation is 2
            assert fl.prop('P & Q').degree() == 2

            # The outermost connective determines the degree
            assert fl.prop('~P & Q').degree() == 2
            assert fl.prop('~(P & Q)').degree() == 1

            # Remember: (P & Q) & R == P & Q & R
            assert fl.prop('(P & Q) & R').degree() == 2
            assert fl.prop('P & Q & R').degree() == 2
            ```
        """
        raise NotImplementedError(
            f"__iter__ is not implemented for '{self.__class__.__name__}'"
        )

    #
    # Proposition Composition Methods
    #

    def __invert__(self, /) -> "Not":
        """Returns [`Not(self)`](./#flogic.Not)."""
        return Not(self)

    def __and__(self, other: "Proposition", /) -> "And":
        """Returns [`And(self, other)`](./#flogic.And) if the other operand is
        a Proposition; otherwise [`NotImplemented`][1].

        [1]: https://docs.python.org/3/library/constants.html#NotImplemented
        """
        if isinstance(other, Proposition):
            return And(self, other)
        return NotImplemented

    def __or__(self, other: "Proposition", /) -> "Or":
        """Returns [`Or(self, other)`](./#flogic.Or) if the other operand is
        a Proposition; otherwise [`NotImplemented`][1].

        [1]: https://docs.python.org/3/library/constants.html#NotImplemented
        """
        if isinstance(other, Proposition):
            return Or(self, other)
        return NotImplemented

    def implies(self, other: "Proposition", /) -> "Implies":
        """Returns [`Implies(self, other)`](./#flogic.Implies)."""
        return Implies(self, other)

    def iff(self, other: "Proposition", /) -> "Iff":
        """Returns [`Iff(self, other)`](./#flogic.Iff)."""
        return Iff(self, other)

    #
    # Interpretation Methods
    #

    @overload
    def __call__(self, vals: Mapping[str, bool], /) -> bool:
        ...

    @overload
    def __call__(self, /, **vals: bool) -> bool:
        ...

    def __call__(self, mapping=None, /, **kwargs) -> bool:
        """Returns the truth value of this proposition under the given
        interpretation.

        Please see the Interpreting section in the `flogic` documentation for
        more information on how to use this operation.

        Returns:
            A boolean representing the truth value of this proposition with
            respect to the given interpretation.

        Raises:
            ValueError: When one of the predicates is interpreted but isn't
                assigned a truth value in the interpretation.
        """
        if mapping is None:
            return self._interpret(kwargs)
        return self._interpret(mapping)

    @abstractmethod
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        """Returns the truth value of this proposition under the given
        interpretation.

        This is an abstract internal method which is delegated to by
        `__call__`. Subclasses must implement this method in order to fully
        implement `__call__`.

        If the interpretation does not assign every (nullary) predicate in this
        proposition to a boolean, then a `ValueError` is raised. This also
        applies in "short circuiting" cases where the second operand doesn't
        need to be interpreted.

        For example, if a interpretation assigns `P` to `True` and does not
        assign `Q` to anything, then interpreting `P | Q` would still raise a
        `ValueError` despite `Q` not needing to be evaluated.
        """
        raise NotImplementedError(
            f"'_interpret' is not implemented for '{self.__class__.__name__}'"
        )

    #
    # String Formatting Methods
    #

    def __repr__(self) -> str:
        """Returns the canonical string representation of this proposition."""
        return f"prop({str(self)!r})"

    # TODO remove later, then replace put __str__ in subclass with new default
    # string formatting implementation
    def __str__(self) -> str:
        return self.formal()

    @abstractmethod
    def formal(self) -> str:
        """Returns the "formal" representation of this proposition. Unlike
        `str(p)`, every binary operation is surrounded with parentheses.

        Example:
            ```python
            import flogic as pl

            s = pl.prop('P & Q & R')
            assert s.formal() == '((P & Q) & R)'
            assert str(s) == 'P & Q & R'
            ```
        """
        raise NotImplementedError(
            f"formal() is not implemented for '{self.__class__.__name__}'"
        )

    #
    # Miscellaneous special methods
    #

    def __bool__(self) -> NoReturn:
        """Raises [`TypeError`][1] because the truth value of a proposition is
        ambiguous. Please use [interpreting][2] instead.

        [1]: https://docs.python.org/3/library/exceptions.html#TypeError
        [2]: ./#flogic.Proposition--interpreting-assigning-truth-values

        """
        raise TypeError(
            "The truth value of a Proposition is ambiguous. Consider using "
            "interpretation through p(**vals)"
        )


_ident_pattern: re.Pattern = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


@dataclass(frozen=True, repr=False)
class Predicate(Proposition):
    """Represents an [predicate][1] in formal logic. Currently, this library
    only supports nullary predicates, which are used to serve as
    [propositional variables][2].

    If the given name is not valid when creating a new instance, then a
    `ValueError` is raised.

    [1]: https://en.wikipedia.org/wiki/Predicate_(mathematical_logic)
    [2]: https://en.wikipedia.org/wiki/Propositional_variable

    Attributes:
        name (str): The name of the formula.
    """

    name: str

    def __post_init__(self):
        if not _ident_pattern.fullmatch(self.name):
            raise ValueError(f"Invalid predicate name: {self.name!r}")

    def __getitem__(self, index: int, /) -> NoReturn:
        raise IndexError(
            f"Predicate has no component propositions; got {index}"
        )

    def __iter__(self, /) -> Iterator[Proposition]:
        return iter(())

    def degree(self, /) -> int:
        return 0

    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        if (truth_value := interpretation.get(self.name)) is not None:
            return truth_value
        raise ValueError(
            f"Predicate '{self.name}' not unassigned when interpreting"
        )

    def formal(self) -> str:
        return self.name

    __str__ = formal


@dataclass(frozen=True, repr=False)
class _LogicOp1(Proposition):
    """Represents a unary (one-place) operation using a
    [logical connective][1].

    [1]: https://en.wikipedia.org/wiki/Logical_connective

    Attributes:
        inner (Proposition): Inner operand.
    """

    inner: Proposition

    def __getitem__(self, index: int, /) -> "Proposition":
        if index == 0:
            return self.inner
        raise IndexError(f"Expected 0; got {index}")

    def __iter__(self, /) -> Iterator["Proposition"]:
        return iter((self.inner,))

    def degree(self) -> int:
        return 1


@dataclass(frozen=True, repr=False)
class Not(_LogicOp1):
    """Represents a [logical negation][1].

    [1]: https://en.wikipedia.org/wiki/Negation

    Attributes:
        inner (Proposition): Inner operand.
    """

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return not self.inner._interpret(i)

    def formal(self) -> str:
        return f"~{self.inner}"

    __str__ = formal


@dataclass(frozen=True, repr=False)
class _LogicOp2(Proposition):
    """Represents a binary (two-place) operation using a
    [logical connective][1].

    [1]: https://en.wikipedia.org/wiki/Logical_connective

    Attributes:
        left (Proposition): Left operand.
        right (Proposition): Right operand.
    """

    left: Proposition
    right: Proposition

    def __getitem__(self, index: int, /) -> "Proposition":
        if index == 0:
            return self.left
        elif index == 1:
            return self.right
        raise IndexError(f"Expected 0 or 1; got {index}")

    def __iter__(self, /) -> Iterator["Proposition"]:
        return iter((self.left, self.right))

    def degree(self) -> int:
        return 2


@dataclass(frozen=True, repr=False)
class And(_LogicOp2):
    """Represents a [logical conjunction][1].

    [1]: https://en.wikipedia.org/wiki/Logical_conjunction

    Attributes:
        left (Proposition): Left conjunct.
        right (Proposition): Right conjunct.
    """

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return self.left._interpret(i) & self.right._interpret(i)

    def formal(self) -> str:
        return f"({self.left} & {self.right})"

    __str__ = formal


@dataclass(frozen=True, repr=False)
class Or(_LogicOp2):
    """Represents a [logical disjunction][1].

    [1]: https://en.wikipedia.org/wiki/Disjunction_(logical_connective)

    Attributes:
        left (Proposition): Left disjunct.
        right (Proposition): Right disjunct.
    """

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return self.left._interpret(i) | self.right._interpret(i)

    def formal(self) -> str:
        return f"({self.left} | {self.right})"

    __str__ = formal


@dataclass(frozen=True, repr=False)
class Implies(_LogicOp2):
    """Represents a [logical material conditional][1].

    [1]: https://en.wikipedia.org/wiki/Material_conditional

    Attributes:
        left (Proposition): Antecedent.
        right (Proposition): Consequent.
    """

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return (not self.left._interpret(i)) | self.right._interpret(i)

    def formal(self) -> str:
        return f"({self.left} -> {self.right})"

    __str__ = formal


@dataclass(frozen=True, repr=False)
class Iff(_LogicOp2):
    """Represents a [logical biconditional][1].

    [1]: https://en.wikipedia.org/wiki/Logical_biconditional

    Attributes:
        left (Proposition): Left operand.
        right (Proposition): Right operand.
    """

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return self.left._interpret(i) is self.right._interpret(i)

    def formal(self) -> str:
        return f"({self.left} <-> {self.right})"


@overload
def atomics(names_sep_by_spaces: str, /) -> tuple[Predicate, ...]:
    ...


@overload
def atomics(name_iterable: Iterable[str], /) -> tuple[Predicate, ...]:
    ...


def atomics(arg: Union[str, Iterable[str]], /) -> tuple[Predicate, ...]:
    if isinstance(arg, str):
        arg = arg.split()
    return tuple(Predicate(name) for name in arg)
