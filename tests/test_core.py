"""Unit Tests for classical-logic/prop.py"""

from collections.abc import Mapping
import pytest
import string
from typing import Iterator

from classical_logic.core import (
    And,
    Predicate,
    Not,
    Proposition,
    Or,
    Implies,
    Iff,
    atomics,
)


simple5: list[Proposition] = [
    Not(Predicate("p")),
    And(Predicate("p"), Predicate("q")),
    Or(Predicate("p"), Predicate("q")),
    Implies(Predicate("p"), Predicate("q")),
    Iff(Predicate("p"), Predicate("q")),
]
# [~p, p&q, p|q, p->q, p<->q]

simple6: list[Proposition] = [Predicate("p"), *simple5]
# [p, ~p, p&q, p|q, p->q, p<->q]

P = Predicate("P")
Q = Predicate("Q")
R = Predicate("R")
S = Predicate("S")
ALL_CHARS_PRED = Predicate(f"_{string.ascii_letters}{string.digits}")

atomic_test_cases: list[Predicate] = [
    Predicate("p"),
    Predicate("ANY_NamE"),
]


class TestAccessing:
    """Tests for the accessing methods."""

    def test_getitem_success(self):
        """Tests p[index]"""
        assert Not(P)[0] is P
        assert And(P, Q)[0] is P
        assert And(P, Q)[1] is Q
        assert Or(P, Q)[0] is P
        assert Or(P, Q)[1] is Q
        assert Implies(P, Q)[0] is P
        assert Implies(P, Q)[1] is Q
        assert Iff(P, Q)[0] is P
        assert Iff(P, Q)[1] is Q

    def test_getitem_index_errors(self):
        with pytest.raises(IndexError):
            P[0]
        with pytest.raises(IndexError):
            P[1]
        with pytest.raises(IndexError):
            P[-1]
        with pytest.raises(IndexError):
            Not(P)[1]
        with pytest.raises(IndexError):
            Not(P)[2]
        with pytest.raises(IndexError):
            Not(P)[-1]
        for cls in [And, Or, Implies, Iff]:
            with pytest.raises(IndexError):
                cls(P, Q)[2]
            with pytest.raises(IndexError):
                cls(P, Q)[3]
            with pytest.raises(IndexError):
                cls(P, Q)[-1]

    def test_iter(self):
        assert list(P) == []
        assert list(Q) == []
        assert list(Not(P)) == [P]
        assert list(Not(Not(P))) == [Not(P)]
        for cls in [And, Or, Implies, Iff]:
            assert list(cls(P, Q)) == [P, Q]
            assert list(cls(cls(P, Q), R)) == [cls(P, Q), R]
            assert list(cls(cls(P, Q), Not(R))) == [cls(P, Q), Not(R)]


class TestDegree:
    """Tests .degree()"""

    def test_degree(self):
        assert P.degree() == 0
        assert Q.degree() == 0
        assert Not(P).degree() == 1
        assert Not(Not(P)).degree() == 1
        assert Not(Not(Not(P))).degree() == 1
        for cls in [And, Or, Implies, Iff]:
            assert cls(P, Q).degree() == 2
            assert cls(cls(P, Q), R).degree() == 2
            assert cls(cls(P, Q), Not(R)).degree() == 2


class TestComposition:
    """Tests for the five composition methods in the Proposition class."""

    samples: list[Proposition] = [P, Not(P), And(P, Q)]

    @pytest.mark.parametrize("u", samples)
    def test_invert(self, u: Proposition):
        assert u.__invert__() == Not(u)
        assert ~u == Not(u)

    @pytest.mark.parametrize("u", samples)
    def test_and(self, u: Proposition):
        for v in self.samples:
            assert u.__and__(v) == And(u, v)
            assert u & v == And(u, v)
            assert v.__and__(u) == And(v, u)
            assert v & u == And(v, u)
        for x in [object(), True, False]:
            assert u.__and__(x) is NotImplemented  # type: ignore
            with pytest.raises(TypeError):
                u & x  # type: ignore
            with pytest.raises(TypeError):
                x & u  # type: ignore

    @pytest.mark.parametrize("u", samples)
    def test_or(self, u: Proposition):
        for v in self.samples:
            assert u.__or__(v) == Or(u, v)
            assert u | v == Or(u, v)
            assert v.__or__(u) == Or(v, u)
            assert v | u == Or(v, u)
        for x in [object(), True, False]:
            assert u.__or__(x) is NotImplemented  # type: ignore
            with pytest.raises(TypeError):
                u | x  # type: ignore
            with pytest.raises(TypeError):
                x | u  # type: ignore

    @pytest.mark.parametrize("u", samples)
    def test_implies(self, u: Proposition):
        for v in self.samples:
            assert u.implies(v) == Implies(u, v)
            assert v.implies(u) == Implies(v, u)

    @pytest.mark.parametrize("u", samples)
    def test_iff(self, u: Proposition):
        for v in self.samples:
            assert u.iff(v) == Iff(u, v)
            assert v.iff(u) == Iff(v, u)


class TestInterpreting:
    """Tests for _interpret() and __call__()."""

    class SampleMapping(Mapping[str, bool]):
        """Sample custom mapping class."""

        def __init__(self, data: dict[str, bool]):
            self.data: dict[str, bool] = data

        def __getitem__(self, name: str) -> bool:
            return self.data[name]

        def __iter__(self) -> Iterator[str]:
            return iter(self.keys())

        def __len__(self) -> int:
            return len(self.data)

    def interpret(self, u: Proposition, interp: dict[str, bool]) -> bool:
        """Interprets in every way, asserts that all values are equal, and then
        returns the value.
        """
        a = u(interp)
        b = u(self.SampleMapping(interp))
        c = u(**interp)
        d = u._interpret(interp)
        assert a is b is c is d
        return a

    def expect_interpret_value_error(
        self, u: Proposition, interp: dict[str, bool]
    ) -> None:
        """Asserts that all interpret will raise a ValueError in every way."""
        with pytest.raises(ValueError):
            u(interp)
        with pytest.raises(ValueError):
            u(self.SampleMapping(interp))
        with pytest.raises(ValueError):
            u(**interp)
        with pytest.raises(ValueError):
            u._interpret(interp)

    @pytest.mark.parametrize("p", [P, ALL_CHARS_PRED])
    def test_predicate_name_present(self, p: Predicate):
        """Tests single predicate cases for when the predicate name is PRESENT
        in the interpretation."""
        assert self.interpret(p, {p.name: True}) is True
        assert self.interpret(p, {p.name: False}) is False

    @pytest.mark.parametrize("p", [P, ALL_CHARS_PRED])
    def test_predicate_name_missing(self, p: Predicate):
        """Tests single predicate cases for when the predicate name is MISSING
        in the interpretation."""
        self.expect_interpret_value_error(p, {})
        self.expect_interpret_value_error(p, {p.name + "2": True})
        self.expect_interpret_value_error(p, {p.name + "2": False})

    def test_not_truth_table(self):
        """Tests truth table of ~P."""
        u = Not(P)
        assert self.interpret(u, {"P": True}) is False
        assert self.interpret(u, {"P": False}) is True

    def test_and_truth_table(self):
        """Tests truth table of P & Q."""
        u = And(P, Q)
        assert self.interpret(u, {"P": True, "Q": True}) is True
        assert self.interpret(u, {"P": True, "Q": False}) is False
        assert self.interpret(u, {"P": False, "Q": True}) is False
        assert self.interpret(u, {"P": False, "Q": False}) is False

    def test_or_truth_table(self):
        """Tests truth table of P | Q."""
        u = Or(P, Q)
        assert self.interpret(u, {"P": True, "Q": True}) is True
        assert self.interpret(u, {"P": True, "Q": False}) is True
        assert self.interpret(u, {"P": False, "Q": True}) is True
        assert self.interpret(u, {"P": False, "Q": False}) is False

    def test_implies_truth_table(self):
        """Tests truth table of P -> Q."""
        u = Implies(P, Q)
        assert self.interpret(u, {"P": True, "Q": True}) is True
        assert self.interpret(u, {"P": True, "Q": False}) is False
        assert self.interpret(u, {"P": False, "Q": True}) is True
        assert self.interpret(u, {"P": False, "Q": False}) is True

    def test_iff_truth_table(self):
        """Tests truth table of P <-> Q"""
        u = Iff(P, Q)
        assert self.interpret(u, {"P": True, "Q": True}) is True
        assert self.interpret(u, {"P": True, "Q": False}) is False
        assert self.interpret(u, {"P": False, "Q": True}) is False
        assert self.interpret(u, {"P": False, "Q": False}) is True

    @pytest.mark.parametrize(
        "u",
        [
            Or(P, Not(P)),  # P | ~P
            Implies(P, P),  # P -> P
            Implies(And(Implies(P, Q), P), Q),  # ((P -> Q) & P) -> Q
            Implies(Implies(Implies(P, Q), P), P),  # ((P -> Q) -> P) -> P
            Iff(
                Iff(P, Q),
                And(Implies(P, Q), Implies(Q, P)),
            ),  # (P <-> Q) <-> ((P -> Q) & (Q -> P))
            Iff(
                Iff(P, Q),
                Or(And(P, Q), And(Not(P), Not(Q))),
            ),  # (P <-> Q) <-> ((P & Q) | (~P & ~Q))
            Implies(
                And(Implies(P, Q), Implies(Not(P), Q)),
                Q,
            ),  # ((P -> Q) & (~P -> Q)) -> Q
        ],
    )
    def test_tautology(self, u: Proposition):
        """Tests if the tautology holds true always."""
        for p in [True, False]:
            for q in [True, False]:
                i = {"P": p, "Q": q}
                assert self.interpret(u, i) is True

    @pytest.mark.parametrize(
        "u",
        [
            And(P, Not(P)),  # P & ~P
            Not(Or(P, Not(P))),  # ~(P | ~P)
            Not(Implies(P, P)),  # ~(P -> P)
            Not(
                Iff(
                    Iff(P, Q),
                    And(Implies(P, Q), Implies(Q, P)),
                )
            ),  # ~( (P <-> Q) <-> ((P -> Q) & (Q -> P)) )
            Not(
                Iff(
                    Iff(P, Q),
                    Or(And(P, Q), And(Not(P), Not(Q))),
                )
            ),  # ~( (P <-> Q) <-> ((P & Q) | (~P & ~Q)) )
        ],
    )
    def test_contradiction(self, u: Proposition):
        """Tests if the contradiction holds false always."""
        for p in [True, False]:
            for q in [True, False]:
                i = {"P": p, "Q": q}
                assert self.interpret(u, i) is False

    @pytest.mark.parametrize(
        "u,interps",
        [
            (
                P,  # Q
                [
                    {},
                    {"Q": True},
                    {"Q": False, "R": True},
                ],
            ),
            (
                Not(P),  # ~P
                [
                    {},
                    {"Q": True},
                ],
            ),
            (
                And(P, Q),  # P & Q
                [
                    {},
                    {"R": True},
                    {"P": False},  # tests short circuiting doesn't work
                    {"Q": False},
                ],
            ),
            (
                Or(P, Q),  # P | Q
                [
                    {},
                    {"R": True},
                    {"P": True},  # tests short circuiting doesn't work
                    {"Q": False},
                ],
            ),
            (
                Implies(P, Q),  # P -> Q
                [
                    {},
                    {"R": True},
                    {"P": False},  # tests short circuiting doesn't work
                    {"Q": False},
                ],
            ),
            (
                Iff(P, Q),  # P <-> Q
                [
                    {},
                    {"R": True},
                    {"P": True},
                    {"Q": False},
                ],
            ),
            (
                Or(
                    And(Not(P), Q),
                    Implies(Iff(P, Q), Q),
                ),  # (~P & Q) | ((P <-> Q) -> Q)
                [
                    {},
                    {"R": True},
                    {"P": True},
                    {"Q": False},
                ],
            ),
        ],
    )
    def test_predicate_missing(
        self, u: Proposition, interps: list[dict[str, bool]]
    ):
        """Tests if a ValueError is raised when there is a unspecified
        predicate."""
        for i in interps:
            self.expect_interpret_value_error(u, i)


class TestStrReprAndFormat:
    """Tests str(p), repr(p), and format(p, spec)."""

    def check_simple(self, u: Proposition, expected: str):
        """Checks the simple represesentation of `u`."""
        assert str(u) == expected
        assert repr(u) == f"prop({expected!r})"
        assert format(u) == expected
        assert format(u, "") == expected
        assert format(u, "S") == expected

    def check_explicit(self, u: Proposition, expected: str):
        """Checks the explicit representation of `u`."""
        assert format(u, "X") == expected

    @pytest.mark.parametrize("p", [P, ALL_CHARS_PRED])
    def test_predicate_nullary(self, p: Predicate):
        self.check_simple(p, p.name)
        self.check_explicit(p, p.name)

    @pytest.mark.parametrize("p", [P, ALL_CHARS_PRED])
    def test_not(self, p: Predicate):
        self.check_simple(Not(p), f"~{p}")
        self.check_explicit(Not(p), f"~{p}")

    @pytest.mark.parametrize("p", [P, ALL_CHARS_PRED])
    def test_binary_explicit(self, p: Predicate):
        self.check_explicit(And(p, p), f"({p} & {p})")
        self.check_explicit(Or(p, p), f"({p} | {p})")
        self.check_explicit(Implies(p, p), f"({p} -> {p})")
        self.check_explicit(Iff(p, p), f"({p} <-> {p})")

    @pytest.mark.parametrize(
        "u,expected",
        [
            (Not(Not(Not(Not(P)))), "~~~~P"),
            (
                Implies(
                    And(Implies(P, Q), P),
                    Q,
                ),
                "(((P -> Q) & P) -> Q)",
            ),
            (
                Iff(
                    Iff(P, Q),
                    And(Implies(P, Q), Implies(Q, P)),
                ),
                "((P <-> Q) <-> ((P -> Q) & (Q -> P)))",
            ),
            (
                Iff(
                    Iff(P, Q),
                    Or(And(P, Q), And(Not(P), Not(Q))),
                ),
                "((P <-> Q) <-> ((P & Q) | (~P & ~Q)))",
            ),
        ],
    )
    def test_complicated_explicit(self, u: Proposition, expected: str):
        self.check_explicit(u, expected)

    @pytest.mark.parametrize("cls,op", [(And, "&"), (Or, "|"), (Iff, "<->")])
    def test_binary_associative_simple(self, cls: type, op: str):
        self.check_simple(
            cls(cls(P, Q), R),
            f"P % Q % R".replace("%", op),
        )
        self.check_simple(
            cls(P, cls(Q, R)),
            f"P % (Q % R)".replace("%", op),
        )
        self.check_simple(
            cls(cls(cls(P, Q), R), S),
            f"P % Q % R % S".replace("%", op),
        )
        self.check_simple(
            cls(P, cls(Q, cls(R, S))),
            f"P % (Q % (R % S))".replace("%", op),
        )
        self.check_simple(
            cls(P, cls(cls(Q, R), S)),
            f"P % (Q % R % S)".replace("%", op),
        )
        self.check_simple(
            cls(cls(P, cls(Q, R)), S),
            f"P % (Q % R) % S".replace("%", op),
        )

    @pytest.mark.parametrize(
        "u,expected",
        [
            (Not(Not(Not(Not(P)))), "~~~~P"),
            (
                Implies(
                    And(Implies(P, Q), P),
                    Q,
                ),
                "((P -> Q) & P) -> Q",
            ),
            (
                Iff(
                    Iff(P, Q),
                    And(Implies(P, Q), Implies(Q, P)),
                ),
                "P <-> Q <-> ((P -> Q) & (Q -> P))",
            ),
            (
                Iff(
                    Iff(P, Q),
                    Or(And(P, Q), And(Not(P), Not(Q))),
                ),
                "P <-> Q <-> ((P & Q) | (~P & ~Q))",
            ),
            (
                Or(
                    Or(
                        And(And(Not(P), Q), R),
                        And(And(Not(P), Not(Q)), R),
                    ),
                    And(P, And(Not(Q), R)),
                ),
                "(~P & Q & R) | (~P & ~Q & R) | (P & (~Q & R))",
            ),
        ],
    )
    def test_complicated_simple(self, u: Proposition, expected: str):
        self.check_simple(u, expected)


class TestBool:
    """Tests bool(p)."""

    @pytest.mark.parametrize("u", [P, Not(P), And(P, Q)])
    def test_bool(self, u):
        """Tests that bool(u) raises TypeError"""
        with pytest.raises(TypeError):
            bool(u)


class TestHash:
    """Tests hash(p)."""

    samples = [P, Not(P), And(P, Q), Or(Iff(P, Q), R), Implies(P, Not(Q))]

    @pytest.mark.parametrize("u", samples)
    @pytest.mark.parametrize("v", samples)
    def test_eq_implies_hash_eq(self, u: Proposition, v: Proposition):
        """Test that p == q implies hash(p) == q and its contrapositive."""
        if u == v:
            assert hash(u) == hash(v)
        if hash(u) != hash(v):
            assert u != v


class TestPredicateCreation:
    """Tests the creation of `Predicate` objects."""

    @pytest.mark.parametrize(
        "name",
        [
            "aName",
            f"{string.ascii_letters}{string.digits}_",
            "_____",
        ],
    )
    def test_valid(self, name: str):
        predicate = Predicate(name)
        assert predicate.name == name

    @pytest.mark.parametrize(
        "name",
        [
            "",
            "another-name",
            "~P",
            "P&Q|R->S<->T",
            "123Cats",
            "Has  Spaces",
            "\uFFFF",
        ],
    )
    def test_invalid(self, name: str):
        with pytest.raises(ValueError):
            Predicate(name)


class TestMisc:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("", ()),
            (" \t\f\r\n", ()),
            ("P", (P,)),
            ("P Q R", (P, Predicate("Q"), Predicate("R"))),
            (
                "apple pear banana",
                (Predicate("apple"), Predicate("pear"), Predicate("banana")),
            ),
            (
                ("apple", "pear", "banana"),
                (Predicate("apple"), Predicate("pear"), Predicate("banana")),
            ),
        ],
    )
    def test_atomics_function(
        self, text: str, expected: tuple[Predicate, ...]
    ):
        assert atomics(text) == expected
