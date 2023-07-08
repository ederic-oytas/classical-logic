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
        "s",
        [
            "abcd",
            "sadfmsoerqwkef",
            "\\'\"\n\t\uFFFF",
        ],
    )
    def test_lex_accept_1(self, s: str):
        """Tests _lex_accept (part 1)"""

        # Assert that each corresponding character in the string
        # will be accepted
        it = iter(s)
        for c in s:
            _lex_accept(it, c)

        # Assert that any more characters will not be accepted
        mes: str = _UNEXP_END_OF_STR
        with pytest.raises(ValueError, match=re.escape(mes)):
            _lex_accept(it, "a")
        with pytest.raises(ValueError, match=re.escape(mes)):
            _lex_accept(it, "b")

    @pytest.mark.parametrize(
        "s,t",
        [
            ("abcd", "efgh"),
            ("abcd", "hijk"),
        ],
    )
    def test_lex_accept_2(self, s: str, t: str):
        """Tests _lex_accept (part 2)"""

        # s: String to iterate on
        # t: Expected characters, which contains incorrect chars

        it = iter(s)

        # Expect that every corresponding character in t is wrong.
        for c, d in zip(s, t):
            mes = _unexp_char(c)
            print(mes)
            with pytest.raises(ValueError, match=re.escape(mes)):
                _lex_accept(it, d)

        # Since the iterator is exhausted, expect we get the end of string
        # error now.
        for c in s:
            mes = _UNEXP_END_OF_STR
            with pytest.raises(ValueError, match=re.escape(mes)):
                _lex_accept(it, c)

    @pytest.mark.parametrize(
        "s,expected_token",
        [
            ("~", (_TokenType.NOT, "~")),
            ("&", (_TokenType.AND, "&")),
            ("|", (_TokenType.OR, "|")),
            ("->", (_TokenType.IMPLIES, "->")),
            ("<->", (_TokenType.IFF, "<->")),
            ("(", (_TokenType.LPARENS, "(")),
            (")", (_TokenType.RPARENS, ")")),
        ],
    )
    def test_individual_operator_and_separator_tokens(
        self, s: str, expected_token: tuple[_TokenType, str]
    ):
        stream = _lex(s)
        assert next(stream) == expected_token
        assert next(stream, None) is None

    @pytest.mark.parametrize(
        "atomic_name",
        [
            "P",
            string.ascii_letters + string.digits + "_",
            "_" * 20 + string.ascii_letters + string.digits,
            string.ascii_uppercase + string.ascii_lowercase,
        ],
    )
    def test_atomic_name_success(self, atomic_name: str):
        assert list(_lex(atomic_name)) == [(_TokenType.ATOMIC, atomic_name)]

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
                    (_TokenType.ATOMIC, "P"),
                    (_TokenType.IMPLIES, "->"),
                    (_TokenType.ATOMIC, "Q"),
                ],
            ),
            (
                "P \t\f\r\n Q R     S",
                [
                    (_TokenType.ATOMIC, "P"),
                    (_TokenType.ATOMIC, "Q"),
                    (_TokenType.ATOMIC, "R"),
                    (_TokenType.ATOMIC, "S"),
                ],
            ),
        ],
    )
    def test_ignore_whitespace(self, s: str, expected_tokens: list[str]):
        """Tests that all whitespace is ignored."""
        assert list(_lex(s)) == expected_tokens

    @pytest.mark.parametrize("c", "0123456789!@#$%^*[]{}\\=")
    def test_individual_unexpected_characters(self, c: str):
        """Test for single unexpected characters"""
        mes = _unexp_char(c)
        with pytest.raises(ValueError, match=re.escape(mes)):
            list(_lex(c))

    @pytest.mark.parametrize(
        "s",
        [
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
        ],
    )
    def test_non_first_unexpected_characters(self, s: str):
        mes = _unexp_char(s[-1])
        with pytest.raises(ValueError, match=re.escape(mes)):
            list(_lex(s))

    @pytest.mark.parametrize(
        "s",
        [
            "-",
            "<",
            "<-",
        ],
    )
    def test_unexpected_end_of_string(self, s: str):
        mes = _UNEXP_END_OF_STR
        with pytest.raises(ValueError, match=re.escape(mes)):
            list(_lex(s))


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
