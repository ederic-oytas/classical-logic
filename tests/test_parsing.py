"""Tests for plogic/parsing.py."""
import pytest
import re
import string

from plogic.parsing import (
    _lex,
    _lex_accept,
    _TokenType,
    _MESSAGE_UNEXPECTED_END_OF_STRING,
    _TEMPLATE_UNEXPECTED_CHARACTER,
)

# TODO finish testing for _lex, _lex_expect

TOKEN_END = (_TokenType.END, "")


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
        mes: str = _MESSAGE_UNEXPECTED_END_OF_STRING
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
            mes: str = _TEMPLATE_UNEXPECTED_CHARACTER.substitute(c=c)
            print(mes)
            with pytest.raises(ValueError, match=re.escape(mes)):
                _lex_accept(it, d)

        # Since the iterator is exhausted, expect we get the end of string
        # error now.
        for c in s:
            mes: str = _MESSAGE_UNEXPECTED_END_OF_STRING
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
        assert next(stream) == (_TokenType.END, "")
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
        assert list(_lex(atomic_name)) == [
            (_TokenType.ATOMIC, atomic_name),
            TOKEN_END,
        ]

    @pytest.mark.parametrize("d", string.digits)
    def test_atomic_name_starting_digit_fail(self, d: str):
        mes = _TEMPLATE_UNEXPECTED_CHARACTER.substitute(c=d)
        with pytest.raises(ValueError, match=re.escape(mes)):
            list(_lex(f"{d}abc"))

    @pytest.mark.parametrize(
        "s,expected_tokens",
        [
            (" ", [TOKEN_END]),
            (" \t\f\r\n", [TOKEN_END]),
            (
                " \t\f\r\n-> \t\f\r\n",
                [
                    (_TokenType.IMPLIES, "->"),
                    TOKEN_END,
                ],
            ),
            (
                "P \t\f\r\n-> \t\f\r\n Q",
                [
                    (_TokenType.ATOMIC, "P"),
                    (_TokenType.IMPLIES, "->"),
                    (_TokenType.ATOMIC, "Q"),
                    TOKEN_END,
                ],
            ),
            (
                "P \t\f\r\n Q R     S",
                [
                    (_TokenType.ATOMIC, "P"),
                    (_TokenType.ATOMIC, "Q"),
                    (_TokenType.ATOMIC, "R"),
                    (_TokenType.ATOMIC, "S"),
                    TOKEN_END,
                ],
            ),
        ],
    )
    def test_ignore_whitespace(self, s: str, expected_tokens: list[str]):
        """Tests that all whitespace is ignored."""
        assert list(_lex(s)) == expected_tokens
