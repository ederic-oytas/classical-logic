"""Unit Tests for flogic/prop.py"""

from itertools import product
import pytest
from typing import Any, Optional

from flogic.core import (
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


class TestPropositionComposition:
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
            assert u.__and__(x) == NotImplemented
            with pytest.raises(TypeError):
                r = u & x
            with pytest.raises(TypeError):
                r = x & u

    @pytest.mark.parametrize("u", samples)
    def test_or(self, u: Proposition):
        for v in self.samples:
            assert u.__or__(v) == And(u, v)
            assert u | v == And(u, v)
            assert v.__or__(u) == And(v, u)
            assert v | u == And(v, u)
        for x in [object(), True, False]:
            assert u.__or__(x) == NotImplemented
            with pytest.raises(TypeError):
                r = u | x
            with pytest.raises(TypeError):
                r = x | u

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


class TestPropositionMiscSpecialMethods:
    @pytest.mark.parametrize("u", simple6)
    def test_bool(self, u):
        """Tests that bool(u) raises TypeError"""
        with pytest.raises(TypeError):
            bool(u)


atomic_test_cases: list[Predicate] = [
    Predicate("p"),
    Predicate("ANY_NamE"),
    Predicate(""),
    Predicate("\\'\"\n\t\uFFFF"),
]


class TestInterpretation:
    """Tests the _interpret methods in the subclasses and __call__ method of
    the Proposition class."""

    Interp = dict[str, bool]

    def interpret3(self, u: Proposition, interp: Interp) -> bool:
        """Interprets in all three ways and asserts that all values are equal,
        and then returns the value.

        The three ways:
            u(mapping)
            u(**vals)
            u._interpret(mapping)
        """
        a = u(interp)
        b = u(**interp)
        c = u._interpret(interp)
        assert a == b == c
        return a

    def expect_interpret_fail(self, u: Proposition, interp: Interp) -> None:
        """Asserts that all interpret will raise a ValueError in all three
        ways."""
        with pytest.raises(ValueError):
            u(interp)
        with pytest.raises(ValueError):
            u(**interp)
        with pytest.raises(ValueError):
            u._interpret(interp)

    @pytest.mark.parametrize("atomic", atomic_test_cases)
    def test_atomic_name_found(self, atomic: Predicate):
        """Tests Atomic._interpret"""
        assert self.interpret3(atomic, {atomic.name: True}) is True
        assert self.interpret3(atomic, {atomic.name: False}) is False

    @pytest.mark.parametrize("atomic", [Predicate("p"), Predicate("q")])
    def test_atomic_name_not_found(self, atomic: Predicate):
        """Tests Atomic._interpret"""
        self.expect_interpret_fail(atomic, {atomic.name + "2": True})
        self.expect_interpret_fail(atomic, {atomic.name + "2": False})

    def test_not_truth_table(self):
        """Tests truth table of ~p"""
        not_p = Not(Predicate("p"))
        assert self.interpret3(not_p, {"p": True}) is False
        assert self.interpret3(not_p, {"p": False}) is True

    def test_and_truth_table(self):
        """Tests truth table of p&q"""
        p_and_q = And(Predicate("p"), Predicate("q"))
        assert self.interpret3(p_and_q, {"p": True, "q": True}) is True
        assert self.interpret3(p_and_q, {"p": True, "q": False}) is False
        assert self.interpret3(p_and_q, {"p": False, "q": True}) is False
        assert self.interpret3(p_and_q, {"p": False, "q": False}) is False

    def test_or_truth_table(self):
        """Tests truth table of p|q"""
        p_or_q = Or(Predicate("p"), Predicate("q"))
        assert self.interpret3(p_or_q, {"p": True, "q": True}) is True
        assert self.interpret3(p_or_q, {"p": True, "q": False}) is True
        assert self.interpret3(p_or_q, {"p": False, "q": True}) is True
        assert self.interpret3(p_or_q, {"p": False, "q": False}) is False

    def test_implies_truth_table(self):
        """Tests truth table of p->q"""
        p_implies_q = Implies(Predicate("p"), Predicate("q"))
        assert self.interpret3(p_implies_q, {"p": True, "q": True}) is True
        assert self.interpret3(p_implies_q, {"p": True, "q": False}) is False
        assert self.interpret3(p_implies_q, {"p": False, "q": True}) is True
        assert self.interpret3(p_implies_q, {"p": False, "q": False}) is True

    def test_iff_truth_table(self):
        """Tests truth table of p<->q"""
        p_iff_q = Iff(Predicate("p"), Predicate("q"))
        assert self.interpret3(p_iff_q, {"p": True, "q": True}) is True
        assert self.interpret3(p_iff_q, {"p": True, "q": False}) is False
        assert self.interpret3(p_iff_q, {"p": False, "q": True}) is False
        assert self.interpret3(p_iff_q, {"p": False, "q": False}) is True

    @pytest.mark.parametrize(
        "u,interp_expected_pairs",
        [
            (
                Not(
                    Not(Not(Not(Predicate("p"))))
                ),  # ~~~~p  (quadruple negation)
                [
                    ({"p": True}, True),
                    ({"p": False}, False),
                ],
            ),
            (
                Or(Predicate("p"), Not(Predicate("p"))),  # p | ~p  (tautology)
                [
                    ({"p": True}, True),
                    ({"p": False}, True),
                ],
            ),
            (
                And(
                    Predicate("p"), Not(Predicate("p"))
                ),  # p & ~p  (contradiction)
                [
                    ({"p": True}, False),
                    ({"p": False}, False),
                ],
            ),
            (
                Implies(
                    And(
                        Implies(Predicate("p"), Predicate("q")), Predicate("p")
                    ),
                    Predicate("q"),
                ),  # ((p->q)&q) -> q  (Modens Ponens, so a tautology)
                [
                    ({"p": True, "q": True}, True),
                    ({"p": True, "q": False}, True),
                    ({"p": False, "q": True}, True),
                    ({"p": False, "q": False}, True),
                ],
            ),
            (
                Iff(
                    Iff(Predicate("p"), Predicate("q")),
                    And(
                        Implies(Predicate("p"), Predicate("q")),
                        Implies(Predicate("q"), Predicate("p")),
                    ),
                ),  # (p <-> q) <-> ((p -> q) & (q -> p))  (tautology)
                [
                    ({"p": True, "q": True}, True),
                    ({"p": True, "q": False}, True),
                    ({"p": False, "q": True}, True),
                    ({"p": False, "q": False}, True),
                ],
            ),
            (
                Iff(
                    Iff(Predicate("p"), Predicate("q")),
                    Or(
                        And(Predicate("p"), Predicate("q")),
                        And(Not(Predicate("p")), Not(Predicate("q"))),
                    ),
                ),  # (p <-> q) <-> ((p & q) | (~p & ~q))  (tautology)
                [
                    ({"p": True, "q": True}, True),
                    ({"p": True, "q": False}, True),
                    ({"p": False, "q": True}, True),
                    ({"p": False, "q": False}, True),
                ],
            ),
        ],
    )
    def test_complex_cases(
        self,
        u: Proposition,
        interp_expected_pairs: list[tuple[Interp, bool]],
    ):
        """Test cases with some nesting."""
        for interp, expected in interp_expected_pairs:
            assert self.interpret3(u, interp) is expected

    @pytest.mark.parametrize(
        "u,interp_expected_pairs",
        [
            (
                And(
                    Or(
                        Implies(Predicate("p"), Predicate("p")),
                        Iff(Predicate("p"), Predicate("p")),
                    ),
                    Not(Predicate("p")),
                ),  # ((p -> p) | (p <-> p)) & ~p
                [
                    ({}, None),
                    ({"x": True}, None),
                ],
            ),
            # The following tests also try to test the "short circuiting"
            # nature of interpreting.
            (
                Not(Predicate("p")),
                [  # ~p
                    ({}, None),
                    ({"x": True}, None),
                    ({"x": False}, None),
                ],
            ),
            (
                And(Predicate("p"), Predicate("q")),  # p & q
                [
                    ({}, None),
                    ({"p": True}, None),
                    ({"p": False}, False),
                    ({"q": True}, None),
                    ({"q": False}, None),
                ],
            ),
            (
                Or(Predicate("p"), Predicate("q")),  # p | q
                [
                    ({}, None),
                    ({"p": True}, True),
                    ({"p": False}, None),
                    ({"q": True}, None),
                    ({"q": False}, None),
                ],
            ),
            (
                Implies(Predicate("p"), Predicate("q")),  # p -> q (== ~p | q)
                [
                    ({}, None),
                    ({"p": True}, None),
                    ({"p": False}, True),
                    ({"q": True}, None),
                    ({"q": False}, None),
                ],
            ),
            (
                Iff(Predicate("p"), Predicate("q")),  # p <-> q
                [
                    ({}, None),
                    ({"p": True}, None),
                    ({"p": False}, None),
                    ({"q": True}, None),
                    ({"q": False}, None),
                ],
            ),
        ],
    )
    def test_complex_atomic_missing(
        self,
        u: Proposition,
        interp_expected_pairs: list[tuple[Interp, Optional[bool]]],
    ):
        """Test cases with some nesting when an atomic value is not assigned"""
        for interp, expected in interp_expected_pairs:
            if expected is None:
                self.expect_interpret_fail(u, interp)
            else:
                assert self.interpret3(u, interp) is expected


class TestStr:
    """Test the __str__ methods of the six subclasses."""

    @pytest.mark.parametrize("atomic", atomic_test_cases)
    def test_atomic(self, atomic: Predicate):
        assert str(atomic) == atomic.name

    @pytest.mark.parametrize("atomic", atomic_test_cases)
    def test_not(self, atomic: Predicate):
        assert str(Not(atomic)) == f"~{atomic}"

    @pytest.mark.parametrize(
        "cls,conn",
        [
            (And, "&"),
            (Or, "|"),
            (Implies, "->"),
            (Iff, "<->"),
        ],
    )
    @pytest.mark.parametrize("a", atomic_test_cases[1:])
    @pytest.mark.parametrize("b", atomic_test_cases[2:])
    def test_binary_conn(
        self, cls: type, conn: str, a: Predicate, b: Predicate
    ):
        assert str(cls(a, b)) == f"({a.name} {conn} {b.name})"

    @pytest.mark.parametrize(
        "u,expected",
        [
            (
                Not(Not(Not(Not(Predicate("p"))))),
                "~~~~p",
            ),
            (
                Implies(
                    And(
                        Implies(Predicate("p"), Predicate("q")), Predicate("p")
                    ),
                    Predicate("q"),
                ),
                "(((p -> q) & p) -> q)",
            ),
            (
                Iff(
                    Iff(Predicate("p"), Predicate("q")),
                    And(
                        Implies(Predicate("p"), Predicate("q")),
                        Implies(Predicate("q"), Predicate("p")),
                    ),
                ),
                "((p <-> q) <-> ((p -> q) & (q -> p)))",
            ),
            (
                Iff(
                    Iff(Predicate("p"), Predicate("q")),
                    Or(
                        And(Predicate("p"), Predicate("q")),
                        And(Not(Predicate("p")), Not(Predicate("q"))),
                    ),
                ),
                "((p <-> q) <-> ((p & q) | (~p & ~q)))",
            ),
        ],
    )
    def test_complex(self, u: Proposition, expected: str):
        assert str(u) == expected


class TestMisc:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("", ()),
            (" \t\f\r\n", ()),
            ("P", (Predicate("P"),)),
            ("P Q R", (Predicate("P"), Predicate("Q"), Predicate("R"))),
            ("1234 %()$&", (Predicate("1234"), Predicate("%()$&"))),
            (
                "apple pear banana",
                (Predicate("apple"), Predicate("pear"), Predicate("banana")),
            ),
            (
                ("apple", "pear", "banana"),
                (Predicate("apple"), Predicate("pear"), Predicate("banana")),
            ),
            (
                ["apple", "pear", "banana", " \t\f\r\n"],
                (
                    Predicate("apple"),
                    Predicate("pear"),
                    Predicate("banana"),
                    Predicate(" \t\f\r\n"),
                ),
            ),
        ],
    )
    def test_atomics_function(
        self, text: str, expected: tuple[Predicate, ...]
    ):
        assert atomics(text) == expected
