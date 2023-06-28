"""Unit Tests for plogic/prop.py"""

from itertools import product
import pytest

from plogic.prop import And, Atomic, Not, Proposition, Or, Implies, Iff


simple5: list[Proposition] = [
    Not(Atomic("p")),
    And(Atomic("p"), Atomic("q")),
    Or(Atomic("p"), Atomic("q")),
    Implies(Atomic("p"), Atomic("q")),
    Iff(Atomic("p"), Atomic("q")),
]
# [~p, p&q, p|q, p->q, p<->q]

simple6: list[Proposition] = [Atomic("p"), *simple5]
# [p, ~p, p&q, p|q, p->q, p<->q]


class TestPropositionCompositionMethods:
    """Tests for the five composition methods in the Proposition class."""

    @pytest.mark.parametrize("u", simple6)
    def test_invert(self, u: Proposition):
        assert u.__invert__() == Not(u)
        assert ~u == Not(u)

    binary_test_cases_with_correct_types = [
        (Atomic("p"), Atomic("q")),  # (p, q)
        *product(simple5, [Atomic("r")]),  # (~p, r), (p&q, r), ...
        *product([Atomic("r")], simple5),  # (r, ~p), (r, p&q), ...
    ]
    binary_test_cases_with_wrong_second_type = [
        *product(simple6, [object(), True, False])
    ]

    @pytest.mark.parametrize("u,v", binary_test_cases_with_correct_types)
    def test_and_correct_type(self, u: Proposition, v: Proposition):
        """Tests (u & v) where u and v are both Proposition's"""
        assert u.__and__(v) == And(u, v)
        assert u & v == And(u, v)

    @pytest.mark.parametrize("u,x", binary_test_cases_with_wrong_second_type)
    def test_and_incorrect_type(self, u: Proposition, x):
        """Tests u.__and__(x) where u is a Proposition, but x is not."""
        assert u.__and__(x) is NotImplemented

    @pytest.mark.parametrize("u,v", binary_test_cases_with_correct_types)
    def test_or_correct_type(self, u: Proposition, v: Proposition):
        """Tests (u | v) where u and v are both Proposition's"""
        assert u.__or__(v) == Or(u, v)
        assert u | v == Or(u, v)

    @pytest.mark.parametrize("u,x", binary_test_cases_with_wrong_second_type)
    def test_or_incorrect_type(self, u: Proposition, x):
        """Tests u.__or__(x) where u is a Proposition, but x is not."""
        assert u.__or__(x) is NotImplemented

    @pytest.mark.parametrize("u,v", binary_test_cases_with_correct_types)
    def test_implies(self, u: Proposition, v: Proposition):
        """Tests u.implies(v) where u and v are both Proposition's"""
        assert u.implies(v) == Implies(u, v)

    @pytest.mark.parametrize("u,v", binary_test_cases_with_correct_types)
    def test_iff(self, u: Proposition, v: Proposition):
        """Tests u.iff(v) where u and v are both Proposition's"""
        assert u.iff(v) == Iff(u, v)


class TestPropositionMiscSpecialMethods:
    @pytest.mark.parametrize("u", simple6)
    def test_bool(self, u):
        """Tests that bool(p) raises TypeError"""
        with pytest.raises(TypeError):
            bool(u)
