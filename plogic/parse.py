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
