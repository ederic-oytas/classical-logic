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
    END = auto()


def _lex(text: str) -> Generator[tuple[_TokenType, str], None, None]:
    it: Iterator[str] = iter(text)
    c: Optional[str] = next(it, None)

    while True:
        if c is None:
            yield (_TokenType.END, "")
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
            raise ValueError(f"unexpected character '{c}'")

        c = next(it, None)


def _lex_accept(it: Iterator[str], expected: str) -> None:
    """Takes the next item from `it` and compares it to `expected`. If `it` has
    no more items or the item is not equal to `expected`, a `ValueError` is
    raised."""

    c = next(it, None)
    if c is None:
        raise ValueError("unexpected end of string")
    if c != expected:
        raise ValueError(f"unexpected character '{c}'")


#
# Parsing
#

#
# API
#


def prop(text: str, /) -> Proposition:
    return Atomic("")
