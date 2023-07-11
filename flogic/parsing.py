"""Module for parsing.

# Grammar Specification (DRAFT)

This section specifies the grammar used to parse strings which represent
propositions for `flogic`. This will cover both the lexical and syntactical
analysis of the grammar.

This grammar may be extended in the future.

## Lexical Analysis

In the lexical analysis, the given string is split up into tokens. In this
grammar, there are nine (9) tokens in total:
- One (1) identifier token: `IDENT`
- Five (5) operator tokens: `~`, `&`, `|`, `->`, and `<->`
- Two (2) separator tokens: `(` and `)`
- One (1) whitespace token: `WS`

Using a modified BNF grammar notation [similar to that in the Python Docs][1],
the tokens are defined as follows:

```
IDENT   ::= /[a-zA-Z_][a-zA-Z0-9_]*/
NOT     ::= "~"
AND     ::= "&"
OR      ::= "|"
IMPLIES ::= "->"
IFF     ::= "<->"
LPARENS ::= "("
RPARENS ::= ")"
WS      ::= /[ \\t\\f\\r\\n]/
```

[1]: https://docs.python.org/3/reference/introduction.html#notation

Whitespace tokens (`WS`) are ignored, so they are not considered in the
syntactical analysis.

For the purpose of clarity, the operator and separator tokens will be notated
by their quoted counterparts (e.g. `"&"` instead of `AND`).

## Syntactical Analysis

The grammar is an LL(1) grammar and defines five (5) rules in total. It is
defined as follows:

```
bic  ::= cond ("<->" cond)*
cond ::= disj ("->" disj)?
disj ::= conj ("|" conj)*
conj ::= unit ("&" unit)*
unit ::= IDENT
         | "~" unit
         | "(" bic ")"
```

Note that this grammar does not reflect the associativity of the operators.

This concludes the grammar specification.
"""
from typing import Generator, Iterator, Optional
from enum import Enum, auto

from .core import And, Predicate, Iff, Implies, Not, Or, Proposition

#
# Messages
#

_UNEXP_END_OF_STR: str = "unexpected end of string"
"""Error message for when the end of the string is encountered
unexpectedly."""


def _unexp_char(c: str) -> str:
    """Returns an error message saying that an unexpected character `c` was
    encountered."""
    return f"unexpected character '{c}'"


def _unexp_token(token_value: str) -> str:
    """Returns an error message saying that an unexpected token `token_value`
    was encountered, where `token_value` is the value of the token."""
    return f"unexpected token '{token_value}'"


#
# Lexical analysis
#


class _TokenType(Enum):
    IDENT = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    IMPLIES = auto()
    IFF = auto()
    LPARENS = auto()
    RPARENS = auto()


def _lex(text: str) -> Generator[tuple[_TokenType, str], None, None]:
    """Yields tokens from lexing the given string (according to the grammar
    specified in the module docstring).

    Raises a `ValueError` if the string ends unexpectedly or has an unexpected
    character.
    """

    it: Iterator[str] = iter(text)
    c: Optional[str] = next(it, None)

    while True:
        if c is None:  # end of string
            return

        elif c == "~":
            yield (_TokenType.NOT, "~")

        elif c == "&":
            yield (_TokenType.AND, "&")

        elif c == "|":
            yield (_TokenType.OR, "|")

        elif c == "-":
            _lex_accept(it, ">")
            yield (_TokenType.IMPLIES, "->")

        elif c == "<":
            _lex_accept(it, "-")
            _lex_accept(it, ">")
            yield (_TokenType.IFF, "<->")

        elif c == "(":
            yield (_TokenType.LPARENS, "(")

        elif c == ")":
            yield (_TokenType.RPARENS, ")")

        elif c in " \t\f\r\n":  # whitespace
            pass

        elif c.isalpha() or c == "_":
            parts = [c]
            c = next(it, None)
            while c is not None and (c.isalnum() or c == "_"):
                parts.append(c)
                c = next(it, None)
            yield (_TokenType.IDENT, "".join(parts))
            continue  # to skip advancing the iterator

        else:
            raise ValueError(_unexp_char(c))

        c = next(it, None)


def _lex_accept(it: Iterator[str], expected: str) -> None:
    """Gets the next char from `it` and raises `ValueError` if the char is not
    equal to `expected`.
    """

    c = next(it, None)
    if c is None:
        raise ValueError(_UNEXP_END_OF_STR)
    if c != expected:
        raise ValueError(_unexp_char(c))


#
# Parsing
#


class _Parser:
    def __init__(self, text: str, /):
        self._token_stream: Iterator[tuple[_TokenType, str]] = _lex(text)
        """Iterator over the tokens to parse."""

        self._current_token_type: Optional[_TokenType]
        self._current_token_value: str

        self._current_token_type, self._current_token_value = next(
            self._token_stream
        )

    def _advance(self) -> None:
        """Advances to the next token."""
        self._current_token_type, self._current_token_value = next(
            self._token_stream, (None, "")
        )

    def bic(self) -> Proposition:
        """Parses rule `bic`."""
        left = self.cond()
        if self._current_token_type is _TokenType.IFF:
            self._advance()
            return Iff(left, self.bic())
        return left

    def cond(self) -> Proposition:
        """Parses rule `cond`."""
        left = self.disj()
        if self._current_token_type is _TokenType.IMPLIES:
            self._advance()
            return Implies(left, self.cond())
        return left

    def disj(self) -> Proposition:
        """Parses rule `disj`."""
        current_prop = self.conj()
        while self._current_token_type is _TokenType.OR:
            self._advance()
            current_prop = Or(current_prop, self.conj())
        return current_prop

    def conj(self) -> Proposition:
        """Parses rule `conj`."""
        current_prop = self.neg()
        while self._current_token_type is _TokenType.AND:
            self._advance()
            current_prop = And(current_prop, self.neg())
        return current_prop

    def neg(self) -> Proposition:
        """Parses rule `neg`"""
        if self._current_token_type is _TokenType.NOT:
            self._advance()
            return Not(self.neg())
        return self.unit()

    def unit(self) -> Proposition:
        """Parses rule `unit`"""
        if self._current_token_type is _TokenType.IDENT:
            atomic = Predicate(self._current_token_value)
            self._advance()
            return atomic

        elif self._current_token_type is _TokenType.LPARENS:
            self._advance()
            prop = self.bic()
            if self._current_token_type is _TokenType.RPARENS:
                self._advance()
                return prop
            # falls through to raise end of string unexpected token

        if self._current_token_type is None:
            raise ValueError(_UNEXP_END_OF_STR)

        else:
            raise ValueError(_unexp_token(self._current_token_value))


#
# API
#


def prop(text: str, /) -> Proposition:
    return _Parser(text).bic()


def props(text: str, /) -> tuple[Proposition, ...]:
    return tuple(prop(s) for s in text.split(","))
