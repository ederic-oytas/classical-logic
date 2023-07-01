"""Module for parsing.

# Syntax Specification (DRAFT)

## Lexical Analysis

In sum, the grammar specifies one identifier token (`ATOMIC`), five operator
tokens (`~`, `&`, `|`, `->`, and `<->`), and two separator tokens (`(`, `)`).

In addition, all whitespace is ignored by the grammar. We consider whitespace
to be any character in `/[ \\t\\f\\r\\n]/`.

We define the tokens as follows:

```
ATOMIC  ::= /[a-zA-Z_][a-zA-Z0-9_]*/
NOT     ::= "~"
AND     ::= "&"
OR      ::= "|"
IMPLIES ::= "->"
IFF     ::= "<->"
LPARENS ::= "("
RPARENS ::= ")"
```

For the purpose of clarity, the operator and separator tokens will be notated
by their quoted counterparts (e.g. `"&"` instead of `AND`).

## Parsing and Transformation

The grammar is parsed using a top-down process.

We define a context-free grammar which can be parsed by a recursive descent
parser. In total, the grammar has six rules.

The grammar is defined as follows:

```
bic  ::= cond ("<->" bic)?
cond ::= disj ("->" cond)?
disj ::= conj ("|" conj)*
conj ::= neg  ("&" neg)*
neg  ::= unit | "~" neg
unit ::= ATOMIC | "(" bic ")"
```

For efficiency, the tokens are immediately parsed into Proposition objects. If
any of the above rules contain two children, then they are grouped using the
corresponding class. For rules `disj` and `conj`, in cases of three or more
children, the propositions grouped such that it associates to the left. For
example, `"(P & Q & R)"` is transformed to
`And(And(Atomic('P'), Atomic('Q')), Atomic('R'))`.

The precedence and associativity of operators is shown in the table below:

Operator | Precedence | Associativity
---------|------------|---------------
`<->`    | 5          | Right
`->`     | 4          | Right
`|`      | 3          | Left
`&`      | 2          | Left
`~`      | 1          | N/A
"""
from typing import Generator, Iterator, Optional
from enum import Enum, auto

from .core import And, Atomic, Iff, Implies, Not, Or, Proposition

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
    ATOMIC = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    IMPLIES = auto()
    IFF = auto()
    LPARENS = auto()
    RPARENS = auto()


def _lex(text: str) -> Generator[tuple[_TokenType, str], None, None]:
    """Yields tokens from lexing the given string (according to the grammar
    specified in the module docstring.)

    If an unexpected character is encountered, then ``ValueError(mes)`` is
    raised where `mes` is ``_unexp_char(c)`` with `c` as the unexpected char.

    If the end of the string is encountered unexpectedly then
    ``ValueError(mes)`` is raised where `mes` is `_UNEXP_END_OF_STR`.
    """

    it: Iterator[str] = iter(text)
    c: Optional[str] = next(it, None)

    while True:
        if c is None:
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
            while c := next(it, None):
                if c.isalnum() or c == "_":
                    parts.append(c)
                else:
                    break
            yield (_TokenType.ATOMIC, "".join(parts))
            continue  # to skip advancing the iterator

        else:
            raise ValueError(_unexp_char(c))

        c = next(it, None)


def _lex_accept(it: Iterator[str], expected: str) -> None:
    """Takes the next item from `it` and compares it to `expected`. If `it` has
    no more items or the item is not equal to `expected`, a `ValueError` is
    raised.

    The messages of the `ValueError` raised is as follows:
    - If end of string, then `_UNEXP_END_OF_STR` is used.
    - If unexpected char, then `_unexp_char(c)` where c is the unexpected char,
      is used.
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
        if self._current_token_type is _TokenType.ATOMIC:
            atomic = Atomic(self._current_token_value)
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
