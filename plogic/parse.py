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
from dataclasses import dataclass
from enum import Enum, auto
from itertools import chain

from .core import Atomic, Proposition

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


_TT_ATOMIC = _TokenType.ATOMIC
_TT_NOT = _TokenType.NOT
_TT_AND = _TokenType.AND
_TT_OR = _TokenType.OR
_TT_IMPLIES = _TokenType.IMPLIES
_TT_IFF = _TokenType.IFF
_TT_LPARENS = _TokenType.LPARENS
_TT_RPARENS = _TokenType.RPARENS


@dataclass(frozen=True)
class _Token:
    """Represents a lexical token."""

    type_: _TokenType
    """The type of this token."""

    value: str = ""
    """Text value of this token. If the token type is not ATOMIC,
    then this is an empty string."""


def _lex(text: str) -> Generator[_Token, None, None]:
    it = iter(text)

    put_back: str = ""

    while True:
        c: Optional[str]
        if put_back:
            c = put_back
            put_back = ""
        else:
            c = next(it, None)

        if c is None:
            return
        elif c.isalpha() or c == "_":
            parts = [c]
            while True:
                c = next(it, None)
                if c is None:
                    yield _Token(_TT_ATOMIC, "".join(parts))
                    return
                if not (c.isalnum() or c == "_"):
                    yield _Token(_TT_ATOMIC, "".join(parts))
                    put_back = c
                    break
                parts.append(c)
        elif c == "~":
            yield _Token(_TT_NOT)
        elif c == "&":
            yield _Token(_TT_AND)
        elif c == "|":
            yield _Token(_TT_OR)
        elif c == "-":
            _expect(it, ">")
            yield _Token(_TT_IMPLIES)
        elif c == "<":
            _expect(it, "-")
            _expect(it, ">")
            yield _Token(_TT_IFF)
        elif c == "(":
            yield _Token(_TT_LPARENS)
        elif c == ")":
            yield _Token(_TT_RPARENS)
        elif c in " \t\f\r\n":
            continue
        else:
            raise ValueError(f"unexpected character: {c}")


def _expect(it: Iterator, expected: str) -> None:
    c = next(it)
    if c is None:
        raise ValueError("unexpected end of string")
    if c != expected:
        raise ValueError(f"unexpected character: {c}")


#
# Parsing
#

#
# API
#


def prop(text: str, /) -> Proposition:
    return Atomic("")
