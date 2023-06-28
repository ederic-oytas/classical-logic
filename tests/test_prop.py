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

    @pytest.mark.parametrize("p", simple6)
    def test_invert(self, p: Proposition):
        assert p.__invert__() == Not(p)
        assert ~p == Not(p)

    binary_test_cases_with_correct_types = [
        (Atomic("p"), Atomic("q")),  # (p, q)
        *product(simple5, [Atomic("r")]),  # (~p, r), (p&q, r), ...
        *product([Atomic("r")], simple5),  # (r, ~p), (r, p&q), ...
    ]
    binary_test_cases_with_wrong_second_type = [
        *product(simple6, [object(), True, False])
    ]

    @pytest.mark.parametrize("t,u", binary_test_cases_with_correct_types)
    def test_and_correct_type(self, t: Proposition, u: Proposition):
        """Tests (t & u) where t and u are both Proposition's"""
        assert t.__and__(u) == And(t, u)
        assert t & u == And(t, u)

    @pytest.mark.parametrize("t,x", binary_test_cases_with_wrong_second_type)
    def test_and_incorrect_type(self, t: Proposition, x):
        """Tests t.__and__(x) where t is a Proposition, but x is not."""
        assert t.__and__(x) is NotImplemented
