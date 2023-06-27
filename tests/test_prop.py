"""Unit Tests for plogic/prop.py"""

import pytest

from plogic.prop import And, Atomic, Not, Proposition, Or, Implies, Iff


class TestPropositionCompositionMethods:
    """Tests for the five composition methods in the Proposition class."""

    @pytest.mark.parametrize(
        "p",
        [
            Atomic("p"),
            Not(Atomic("p")),
            And(Atomic("p"), Atomic("q")),
            Or(Atomic("p"), Atomic("q")),
            Implies(Atomic("p"), Atomic("q")),
            Iff(Atomic("p"), Atomic("q")),
            Iff(
                And(Atomic("p"), Implies(Atomic("q"), Atomic("r"))),
                Or(Not(Atomic("r")), Atomic("s")),
            ),
        ],
    )
    def test_invert(self, p: Proposition):
        assert p.__invert__() == Not(p)
        assert ~p == Not(p)
