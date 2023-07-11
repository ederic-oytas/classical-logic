"""Tests for flogic/parsing.py."""
import pytest
import re
import string
from flogic.core import And, Predicate, Iff, Implies, Not, Or, Proposition

from flogic.parsing import (
    _lex,
    _lex_accept,
    _TokenType,
    _UNEXP_END_OF_STR,
    _unexp_char,
    prop,
    props,
)

# TODO finish testing for _lex, _lex_expect


class TestLex:
    @pytest.mark.parametrize(
        "text",
        [
            "abcd",
            "sadfmsoerqwkef",
            "\\'\"\n\t\uFFFF",
        ],
    )
    def test_lex_accept(self, text: str):
        """Tests _lex_accept"""

        # Every corresponding character should be accepted
        it = iter(text)
        for c in text:
            _lex_accept(it, c)

        # Do it again but with wrong chars
        it = iter(text)
        for c in text:
            d = chr(ord(c) + 1)
            with pytest.raises(ValueError):
                _lex_accept(it, d)

        # Assert that any more characters will not be accepted
        with pytest.raises(ValueError):
            _lex_accept(it, "a")
        with pytest.raises(ValueError):
            _lex_accept(it, "b")

    @pytest.mark.parametrize(
        "text,expected_token_type",
        [
            # Predicate names:
            ("P", _TokenType.IDENT),
            (f"_{string.ascii_letters}{string.digits}", _TokenType.IDENT),
            # Operators:
            ("~", _TokenType.NOT),
            ("&", _TokenType.AND),
            ("|", _TokenType.OR),
            ("->", _TokenType.IMPLIES),
            ("<->", _TokenType.IFF),
            # Separators:
            ("(", _TokenType.LPARENS),
            (")", _TokenType.RPARENS),
        ],
    )
    def test_lex_single(self, text: str, expected_token_type: _TokenType):
        assert list(_lex(text)) == [(expected_token_type, text)]

    @pytest.mark.parametrize("d", string.digits)
    def test_atomic_name_starting_digit_fail(self, d: str):
        mes = _unexp_char(d)
        with pytest.raises(ValueError, match=re.escape(mes)):
            list(_lex(f"{d}abc"))

    @pytest.mark.parametrize(
        "s,expected_tokens",
        [
            (" ", []),
            (" \t\f\r\n", []),
            (
                " \t\f\r\n-> \t\f\r\n",
                [(_TokenType.IMPLIES, "->")],
            ),
            (
                "P \t\f\r\n-> \t\f\r\n Q",
                [
                    (_TokenType.IDENT, "P"),
                    (_TokenType.IMPLIES, "->"),
                    (_TokenType.IDENT, "Q"),
                ],
            ),
            (
                "P \t\f\r\n Q R     S",
                [
                    (_TokenType.IDENT, "P"),
                    (_TokenType.IDENT, "Q"),
                    (_TokenType.IDENT, "R"),
                    (_TokenType.IDENT, "S"),
                ],
            ),
        ],
    )
    def test_ignore_whitespace(self, s: str, expected_tokens: list[str]):
        """Tests that all whitespace is ignored."""
        assert list(_lex(s)) == expected_tokens

    @pytest.mark.parametrize(
        "text",
        [
            # Single unexpected character tests
            *list("0123456789!@#$%^*[]{}\\="),
            # Tests with unexpected character elsewhere in text
            "-<",
            "--",
            "-P",
            "<<",
            "<=",
            "<P",
            "<--",
            "<-<",
            "<-=",
            "<-P",
            "P Q 0",
            "P Q 12349",
            # Tests that unexpectedly reach end of string
            "-",
            "<",
            "<-",
        ],
    )
    def test_raises_value_error(self, text: str):
        """Tests that lexing the text raises ValueError"""
        with pytest.raises(ValueError):
            list(_lex(text))


P = Predicate("P")
Q = Predicate("Q")
R = Predicate("R")
S = Predicate("S")
T = Predicate("T")


prop_test_cases: list[tuple[str, Proposition]] = [
    # Atomic cases:
    ("P", Predicate("P")),
    ("_abcdefghi", Predicate("_abcdefghi")),
    # Simple connection cases:
    ("~P", Not(P)),
    ("P & Q", And(P, Q)),
    ("P | Q", Or(P, Q)),
    ("P -> Q", Implies(P, Q)),
    ("P <-> Q", Iff(P, Q)),
    # Repeated negation cases:
    ("~~P", Not(Not(P))),
    ("~~~~~P", Not(Not(Not(Not(Not(P)))))),
    # Left associativity cases:
    ("P & Q & R", And(And(P, Q), R)),
    ("P & Q & R & S", And(And(And(P, Q), R), S)),
    ("P | Q | R", Or(Or(P, Q), R)),
    ("P | Q | R | S", Or(Or(Or(P, Q), R), S)),
    # Right associativity cases
    ("P -> Q -> R", Implies(P, Implies(Q, R))),
    ("P -> Q -> R -> S", Implies(P, Implies(Q, Implies(R, S)))),
    ("P <-> Q <-> R", Iff(P, Iff(Q, R))),
    ("P <-> Q <-> R <-> S", Iff(P, Iff(Q, Iff(R, S)))),
    # Precedence cases:
    ("~P & ~Q", And(Not(P), Not(Q))),
    ("~P | ~Q", Or(Not(P), Not(Q))),
    ("~P -> ~Q", Implies(Not(P), Not(Q))),
    ("~P <-> ~Q", Iff(Not(P), Not(Q))),
    (
        "P <-> Q -> R | S & ~T",
        Iff(
            P,
            Implies(
                Q,
                Or(
                    R,
                    And(
                        S,
                        Not(T),
                    ),
                ),
            ),
        ),
    ),
    (
        "~P & Q | R -> S <-> T",
        Iff(
            Implies(
                Or(And(Not(P), Q), R),
                S,
            ),
            T,
        ),
    ),
    (
        "P&Q -> P|Q <-> P|Q -> P&Q",
        Iff(
            Implies(And(P, Q), Or(P, Q)),
            Implies(Or(P, Q), And(P, Q)),
        ),
    ),
    (
        "P&Q | P&~Q -> ~P&Q | ~P&~Q <-> R",
        Iff(
            Implies(
                Or(And(P, Q), And(P, Not(Q))),
                Or(And(Not(P), Q), And(Not(P), Not(Q))),
            ),
            R,
        ),
    ),
    # Precedence and associativity cases:
    (
        "P&Q&R | P&Q&R | P&Q&R",
        Or(
            Or(
                And(And(P, Q), R),
                And(And(P, Q), R),
            ),
            And(And(P, Q), R),
        ),
    ),
    (
        "P|Q|R -> P|Q|R -> P|Q|R",
        Implies(
            Or(Or(P, Q), R),
            Implies(
                Or(Or(P, Q), R),
                Or(Or(P, Q), R),
            ),
        ),
    ),
    (
        "P->Q->R <-> P->Q->R <-> P->Q->R",
        Iff(
            Implies(P, Implies(Q, R)),
            Iff(
                Implies(P, Implies(Q, R)),
                Implies(P, Implies(Q, R)),
            ),
        ),
    ),
    # Parentheses cases:
    ("P & (Q & R)", And(P, And(Q, R))),
    ("(P & Q) & R", And(And(P, Q), R)),
    ("P | (Q | R)", Or(P, Or(Q, R))),
    ("(P | Q) | R", Or(Or(P, Q), R)),
    ("P -> (Q -> R)", Implies(P, Implies(Q, R))),
    ("(P -> Q) -> R", Implies(Implies(P, Q), R)),
    ("P <-> (Q <-> R)", Iff(P, Iff(Q, R))),
    ("(P <-> Q) <-> R", Iff(Iff(P, Q), R)),
    ("P <-> (((((Q <-> R)))))", Iff(P, Iff(Q, R))),
    ("P <-> ((((( (((((Q <-> R))))) )))))", Iff(P, Iff(Q, R))),
]


class TestProp:
    @pytest.mark.parametrize("text,expected", prop_test_cases)
    def test_prop(self, text, expected):
        """Tests `prop`"""
        assert prop(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("P", (P,)),
            ("P, Q, R", (P, Q, R)),
            (
                "~P, P|Q, P&Q, P->Q, P<->Q",
                (Not(P), Or(P, Q), And(P, Q), Implies(P, Q), Iff(P, Q)),
            ),
        ],
    )
    def test_props(self, text, expected):
        """Tests `props`"""
        assert props(text) == expected
