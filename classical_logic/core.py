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
from typing import ClassVar, overload, Literal, NoReturn, Union


class Proposition(ABC):
    """Represents a logical proposition. This type serves as the base class
    for all proposition types in the `classical-logic` package.

    # Operation Summary

    The following table summarizes the special operations on this class:

    Operation          | Description
    -------------------|---------------------------------------------------
    `#!py p[i]`        | Gets the component at index `i` of `p`. Raises [`IndexError`][IndexError] if index is out of range.
    `#!py iter(p)`     | Returns an iterator over the (immediate) components of `p`.
    `#!py ~p`          | Returns [`Not(p)`][classical_logic.Not].
    `#!py p & q`       | Returns [`And(p, q)`][classical_logic.And].
    `#!py p | q`       | Returns [`Or(p, q)`][classical_logic.Or].
    `#!py p(mapping)` <br> `#!py p(**kwargs)`  | Interprets `p`. See [Interpreting][interpreting] for more information.
    `#!py p == q`      | Checks if `p` and `q` are structurally equal.
    `#!py p != q`      | Checks if `p` and `q` are not structurally equal.
    `#!py hash(p)`     | Returns the hash value of `p`.
    `#!py str(p)`      | Returns a parsable string representation of `p`. See [Formatting][formatting] for more information.
    `#!py repr(p)`     | Returns the canonical string representation of `p`. See [Formatting][formatting] for more information.
    `#!py format(p, spec)` | Returns a formatted string representation of `p`. See [Formatting][formatting] for more information.

    **Note:** `bool(p)` is not supported as the truth value of a proposition is
    ambiguous.
    """  # noqa: E501

    """

    OLD DOCUMENTATION; MAYBE MOVE TO USER GUIDE

    # Class Hierarchy

    The following is the class hierarchy for the `classical-logic` package:

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

    The [`Not`](./#classical-logic.Not), [`And`](./#classical-logic.And), [`Or`](./#classical-logic.Or),
    [`Implies`](./#classical-logic.Implies), and [`Iff`](./#classical-logic.Iff) classes are all
    data classes, whose instances are composed of propositions.

    A `Not` object represents a logical negation and can be created using a
    single proposition: `Not(inner)`.

    `And`, `Or`, `Implies`, and `Iff` objects represent binary logical
    operations and can be created using two propositions. For example:
    `And(left, right)`.

    The [`UnaryConnection`](./#classical-logic.UnaryConnection) and
    [`BinaryConnection`](./#classical-logic.BinaryConnection) classes act as the
    abstract base classes for propositions constructed using unary and binary
    [logical connectives](https://en.wikipedia.org/wiki/Logical_connective).


    # Composing Compound Propositions

    This class provides five operations/methods to compose compound
    propositions:

    ## `~p`

    Returns [`Not(p)`](./#classical-logic.Not).

    ## `p & q`

    Returns [`And(p, q)`](./#classical-logic.And).

    ## `p | q`

    Returns [`Or(p, q)`](./#classical-logic.Or).

    ## `p.implies(q)`

    Returns [`Implies(p, q)`](./#classical-logic.Implies).

    ## `p.iff(q)`

    Returns [`Iff(p, q)`](./#classical-logic.Iff).

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
        import classical-logic as pl

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
        import classical-logic as pl

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
        import classical-logic as pl

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
    [Interpreting](./#classical-logic.Proposition--interpreting-assigning-truth-values)
    section to learn how to assign truth values.

    """  # noqa: E501

    #
    # Accessing Methods
    #

    @abstractmethod
    def __getitem__(self, index: int, /) -> "Proposition":
        """Returns the component proposition at the given index. Raises
        `IndexError` when index is out of range.

        Example:

            ```python
            import classical_logic as cl

            p = cl.prop('P & Q')
            assert p[0] == cl.prop('P')
            assert p[1] == cl.prop('Q')
            ```
        """
        raise NotImplementedError(
            f"__getitem__ is not implemented for '{self.__class__.__name__}'"
        )

    @abstractmethod
    def __iter__(self, /) -> Iterator["Proposition"]:
        """Returns an iterator over the component propositions.

        Example:

            ```python
            import classical_logic as cl

            p = cl.prop('P & Q')
            it = iter(p)
            assert next(it, None) == cl.prop('P')
            assert next(it, None) == cl.prop('Q')
            assert next(it, None) is None
            ```
        """
        raise NotImplementedError(
            f"__iter__ is not implemented for '{self.__class__.__name__}'"
        )

    #
    # Degree method
    #

    @abstractmethod
    def degree(self, /) -> int:
        """Returns the number of immediate component propositions this
        proposition contains.

        For example, a negation (`~P`) has a degree of `1` because it's a
        unary (two-place) operation, which takes one operand.

        A conjunction (`P & Q`) and a disjunction (`P | Q`) both have degrees
        of `2`, because they are both binary (two-place) operations.

        A predicate (`P`) has a degree of `0`, since it doesn't contain any
        components.

        Example:
            ```python
            import classical_logic as cl


            # Degree of a predicate is 0
            assert cl.prop('P').degree() == 0

            # Degree of a negation is 1
            assert cl.prop('~P').degree() == 1

            # The outermost connective determines the degree
            assert cl.prop('~~~P').degree() == 1
            assert cl.prop('~(~~P)').degree() == 1

            # Degree of a binary (two-place) operation is 2
            assert cl.prop('P & Q').degree() == 2

            # The outermost connective determines the degree
            assert cl.prop('~P & Q').degree() == 2
            assert cl.prop('~(P & Q)').degree() == 1

            # Remember: (P & Q) & R == P & Q & R
            assert cl.prop('(P & Q) & R').degree() == 2
            assert cl.prop('P & Q & R').degree() == 2
            ```
        """
        raise NotImplementedError(
            f"__iter__ is not implemented for '{self.__class__.__name__}'"
        )

    #
    # Proposition Composition Methods
    #

    def __invert__(self, /) -> "Not":
        """Returns [`Not(self)`](./#classical-logic.Not)."""
        return Not(self)

    def __and__(self, other: "Proposition", /) -> "And":
        """Returns [`And(self, other)`](./#classical-logic.And) if the other
        operand is a Proposition; otherwise [`NotImplemented`][1].

        [1]: https://docs.python.org/3/library/constants.html#NotImplemented
        """
        if isinstance(other, Proposition):
            return And(self, other)
        return NotImplemented

    def __or__(self, other: "Proposition", /) -> "Or":
        """Returns [`Or(self, other)`](./#classical-logic.Or) if the other
        operand is a Proposition; otherwise [`NotImplemented`][1].

        [1]: https://docs.python.org/3/library/constants.html#NotImplemented
        """
        if isinstance(other, Proposition):
            return Or(self, other)
        return NotImplemented

    def implies(self, other: "Proposition", /) -> "Implies":
        """Returns [`Implies(self, other)`](./#classical-logic.Implies)."""
        return Implies(self, other)

    def iff(self, other: "Proposition", /) -> "Iff":
        """Returns [`Iff(self, other)`](./#classical-logic.Iff)."""
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
        """Interprets the proposition.

        Please see the Interpreting section in the `classical-logic`
        documentation for more information on how to use this operation.

        Returns:
            A boolean representing the truth value of this proposition with
            respect to the given interpretation.

        Raises:
            ValueError: One of the predicates was not assigned a truth value in
                the interpretation.
        """
        if mapping is None:
            return self._interpret(kwargs)
        return self._interpret(mapping)

    @abstractmethod
    def _interpret(self, interpretation: Mapping[str, bool], /) -> bool:
        """Returns the truth value of this proposition under the given
        interpretation. Raises `ValueError` when one of the predicates in the
        proposition is not specified, even if the predicate need not to be
        evaluated (do not short circuit).

        This is an abstract internal method which is delegated to by
        `__call__`. Subclasses must implement this method in order to fully
        implement `__call__`.

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

    def __format__(self, format_spec: str, /) -> str:
        """Returns a string representation of this proposition formatted
        according to the given specification.

        Currently, this method accepts either 'S', 'X', or '' (empty string)
        as the argument. The following describe the different arguments:

        - 'S': Simple mode. All binary operations are surrounded with
            parentheses, but are omitted in two cases:
            - The binary operation is the outermost operation.
            - The binary operation is associative and is the left operand of
                a binary operation of the same type. For example, (P & Q) & R
                is represented as 'P & Q & R'. However, it is not omitted in
                P & (Q & R), because it represents a structurally different
                proposition.

        - 'X': Explicit mode. All binary operations are surrounded with
            parentheses always.

        - '': Default to 'S' (Simple mode)

        This method raises `ValueError` upon receiving an incorrect format
        spec.
        """
        if format_spec == "X":
            return self._explicit_str()
        elif format_spec in ("S", ""):
            return str(self)
        raise ValueError(f"Invalid format specification: {format_spec!r}")

    @abstractmethod
    def _explicit_str(self) -> str:
        """Returns the "explicit" representation of this proposition, in which
        every binary operation is surrounded with parentheses, always.

        Example:
            ```python
            import classical-logic as pl

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
        [2]: ./#classical_logic.Proposition--interpreting-assigning-truth-values

        """  # noqa: E501
        raise TypeError(
            "The truth value of a Proposition is ambiguous. Consider using "
            "interpretation through p(**vals)"
        )


_ident_pattern: re.Pattern = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


@dataclass(frozen=True, repr=False)
class Predicate(Proposition):
    """Represents an [predicate][1] in formal logic. Currently,
    `classical-logic` only supports nullary (0-argument) predicates, which are
    used to serve as [propositional variables][2].

    When creating a new instance, if the given name is not valid, a
    [`ValueError`][ValueError] is raised.

    [1]: https://en.wikipedia.org/wiki/Predicate_(mathematical_logic)
    [2]: https://en.wikipedia.org/wiki/Propositional_variable

    Attributes:
        name (str): The name of the predicate.
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

    def _explicit_str(self) -> str:
        return self.name

    __str__ = _explicit_str


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
    """Represents a [logical negation][1], which is interpreted to be *true*
    just in the case that its operand is *false*.

    Truth table of `~P`:

    | `P`   | `~P`  |
    |-------|-------|
    | **T** | *F*   |
    | *F*   | **T** |

    [1]: https://en.wikipedia.org/wiki/Negation

    Attributes:
        inner (Proposition): Inner operand.
    """

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return not self.inner._interpret(i)

    def _explicit_str(self) -> str:
        return f"~{self.inner}"

    __str__ = _explicit_str


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

    @property
    @abstractmethod
    def _operator(self) -> str:
        """Operator symbol for this binary operation."""

    @property
    @abstractmethod
    def _associative(self) -> bool:
        """True if this binary operation is associative, False otherwise."""

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

    def __str__(self) -> str:
        a: str
        if self._associative and type(self.left) is type(self):
            a = str(self.left)
        elif isinstance(self.left, _LogicOp2):
            a = f"({self.left})"
        else:
            a = str(self.left)

        b: str
        if isinstance(self.right, _LogicOp2):
            b = f"({self.right})"
        else:
            b = str(self.right)

        return f"{a} {self._operator} {b}"

    def _explicit_str(self) -> str:
        a = self.left._explicit_str()
        b = self.right._explicit_str()
        return f"({a} {self._operator} {b})"

    # Overridden hash to account for the object type in computing a hash, for
    # efficiency. This is done because under the default generated __hash__,
    # objects such as Or(P, Q) and And(P, Q) would have the same hash despite
    # being different classes.
    def __hash__(self) -> int:
        return hash((type(self), self.left, self.right))


@dataclass(frozen=True, repr=False)
class And(_LogicOp2):
    """Represents a [logical conjunction][1], which is interpreted to be *true*
    just in the case that *both of its operands are true*.

    Truth table of `P & Q`:

    | `P`   | `Q`   | `P & Q` |
    |-------|-------|---------|
    | **T** | **T** | **T**   |
    | **T** | *F*   | *F*     |
    | *F*   | **T** | *F*     |
    | *F*   | *F*   | *F*     |

    [1]: https://en.wikipedia.org/wiki/Logical_conjunction

    Attributes:
        left (Proposition): Left conjunct.
        right (Proposition): Right conjunct.
    """

    _associative: ClassVar[bool] = True
    _operator: ClassVar[str] = "&"

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return self.left._interpret(i) & self.right._interpret(i)


@dataclass(frozen=True, repr=False)
class Or(_LogicOp2):
    """Represents a [logical disjunction][1], which is interpreted to be *true*
    just in the case that *at least one of its operands is true*.

    Truth table of `P | Q`:

    | `P`   | `Q`   | `P | Q` |
    |-------|-------|---------|
    | **T** | **T** | **T**   |
    | **T** | *F*   | **T**   |
    | *F*   | **T** | **T**   |
    | *F*   | *F*   | *F*     |

    [1]: https://en.wikipedia.org/wiki/Disjunction_(logical_connective)

    Attributes:
        left (Proposition): Left disjunct.
        right (Proposition): Right disjunct.
    """

    _associative: ClassVar[bool] = True
    _operator: ClassVar[str] = "|"

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return self.left._interpret(i) | self.right._interpret(i)


@dataclass(frozen=True, repr=False)
class Implies(_LogicOp2):
    """Represents a [logical material conditional][1], which is interpreted to
    be *true* just in the case *its first operand is false or both of its
    operands are true.*

    Truth table of `P -> Q`:

    | `P`   | `Q`   | `P -> Q` |
    |-------|-------|----------|
    | **T** | **T** | **T**    |
    | **T** | *F*   | *F*      |
    | *F*   | **T** | **T**    |
    | *F*   | *F*   | **T**    |

    [1]: https://en.wikipedia.org/wiki/Material_conditional

    Attributes:
        left (Proposition): Antecedent.
        right (Proposition): Consequent.
    """

    _associative: ClassVar[bool] = False
    _operator: ClassVar[str] = "->"

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return (not self.left._interpret(i)) | self.right._interpret(i)


@dataclass(frozen=True, repr=False)
class Iff(_LogicOp2):
    """Represents a [logical biconditional][1], which is interpreted to be
    *true* just in the case that *both of its operands share the same truth
    value*.

    Truth table of `P & Q`:

    | `P`   | `Q`   | `P <-> Q` |
    |-------|-------|-----------|
    | **T** | **T** | **T**     |
    | **T** | *F*   | *F*       |
    | *F*   | **T** | *F*       |
    | *F*   | *F*   | **T**     |

    [1]: https://en.wikipedia.org/wiki/Logical_biconditional

    Attributes:
        left (Proposition): Left operand.
        right (Proposition): Right operand.
    """

    _associative: ClassVar[bool] = True
    _operator: ClassVar[str] = "<->"

    def _interpret(self, i: Mapping[str, bool], /) -> bool:
        return self.left._interpret(i) is self.right._interpret(i)


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
