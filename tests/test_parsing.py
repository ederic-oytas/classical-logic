"""Tests for plogic/parsing.py."""
import pytest
import re

from plogic.parsing import (
    _lex_accept,
    _MESSAGE_UNEXPECTED_END_OF_STRING,
    _TEMPLATE_UNEXPECTED_CHARACTER,
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
