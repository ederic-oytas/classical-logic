
# User Guide

## Installation

Install the package using Pip:

```bash
pip install classical-logic
```

## Creating Propositions with `prop()` and `props()`

The preferred way to create a proposition is through the `prop()` function:

```python
u = prop('P')
v = prop('P & ~Q')
w = prop('P & Q | ~R -> S')
```

Every operator has a precedence to them. Here is a table of each operator's precedence. The operators with higher precedence are evaluated first.

| Operation     | Symbolically            | Precedence |
| ------------- | ----------------------- | ---------- |
| Negation      | `~P`                    | 5          |
| Disjunction   | <code>P &#124; Q</code> | 4          |
| Conjunction   | `P & Q`                 | 3          |
| Conditional   | `P -> Q`                | 2          |
| Biconditional | `P <-> Q`               | 1          |

When two of the same operator chained together, they are evaluated from left to right, that is, they are left-associative. For example:

```python
assert prop('P & Q & R')     == prop('(P & Q) & R')
assert prop('P | Q | R')     == prop('(P | Q) | R')
assert prop('P -> Q -> R')   == prop('(P -> Q) -> R')
assert prop('P <-> Q <-> R') == prop('(P <-> Q) <-> R')
```

You are also not limited to single characters as well. You can use letters, underscores, and numbers (not at the start of a name).

```python
u1 = prop('boom & bust')
u2 = prop('Rain | shine')
u3 = prop('snake_case | camelCase | PascalCase')
u4 = prop('numbers12345')

# Note: Does not work because it starts with a number
# u5 = prop('2cats')
```

You can also create multiple propositions using `props()`. Each proposition is separated by commas (`,`).

```python
us = props('P, Q, P & Q')

# You can also use unpacking
p, q, r = props('P, Q, R')
```

## Composing Propositions

You can use the `|` and `&` operators to create disjunctions and conjunctions. For example:

```python
p = prop('P')
q = prop('Q')

assert p & q == prop('P & Q')
assert p | q == prop('P | Q')

assert p & q | q & p == prop('(P & Q) | (Q & P)')
```

You can use the `implies` and `iff` methods ot create conditionals and biconditionals. For example:

```python
p = prop('P')
q = prop('Q')

assert p.implies(q) == prop('P -> Q')
assert p.iff(q)     == prop('P <-> Q')

assert p.implies(q).iff(q) == prop('(P -> Q) <-> Q')
```

You can use these together to form even more complex propositions:

```python
p = prop('P')
q = prop('Q')

assert (p | q).implies(p & q) == prop('(P | Q) -> (P & Q)')
```

## Indexing

You can use index notation to select a particular component of a compound proposition. For example:

```python
u = prop('P & (Q | R)')
assert u[0] == prop('P')
assert u[1] == prop('Q | R')
assert u[1][0] == prop('Q')
assert u[1][1] == prop('R')
```

You can also use it to get the inside of a negation:

```python
u = prop('~~P')
assert u[0] == prop('~P')
assert u[0][0] == prop('P')
```

## Unpacking

This package also supports Python's unpacking syntax. For example:

```python
u = prop('P & (Q | R)')

left, right = u
assert left == prop('P')
assert right == prop('Q | R')

# You can also unpack further:
p, (q, r) = u
assert p == prop('P')
assert q == prop('Q')
assert r == prop('R')
```

## Interpreting

We can assign each predicate (name) in a proposition to truth values by calling the predicate. For example:

```python
u = prop('P & Q')

assert u(P=True, Q=True) is True
assert u(P=True, Q=False) is False
assert u(P=False, Q=True) is False
assert u(P=False, Q=False) is False
```

All predicates must be assigned to a truth value, otherwise a `ValueError` is raised.

```python
u = prop('P & Q')

# These raise ValueError since one of the propositions isn't specified.
u(P=True)
u(Q=True)
```

You can also give a dictionary or any kind of mapping as an argument.

```python
u = prop('P & Q')

d = {'P': True, 'Q': True}
assert u(d) is True
assert u({'P': True, 'Q': True}) is True
```

## Formatting

You can use `str` to serialize a proposition object into a string:

```python
print(str(prop('P & Q | R')))  # (P & Q) | R
print(str(prop('P & (Q | R)')))  # P & (Q | R)
```

This string can be parsed back into a proposition object:

```python
u = prop('P <-> Q')
text = str(u)
v = prop(text)
assert u == v
```

You can use f-strings to format propositions into strings.

```python
u = prop('P & Q')
print(f"This is a conjunction: {u}")
```

There are also two modes for formatting: **Simple** and **Explicit**.

*Simple* mode is the mode used by default. In this mode, we preserve all parentheses around binary operations except:

1. The outermost parentheses

2. Parentheses in an left-associative chain of the same operator.

For example:

```python
print(prop('(P & Q)'))        # prints as 'P & Q', without the parentheses!
print(prop('((P & Q) & R)'))  # prints as 'P & Q & R' instead of '(P & Q) & R'
print(prop('(P & (Q & R))'))  # prints as 'P & (Q & R)', NOT 'P & Q & R'
                              # since operations associate to the left
```

You can explicitly print a proposition in simple mode using 'S' as the format spec. For example:

```python
u = prop('P & Q')
print(f"This is a conjunction: {u}")    # implicit
print(f"This is a conjunction: {u:}")   # explicit w/ empty format spec
print(f"This is a conjunction: {u:S}")  # explicit with letter 'S'
```

*Explicit* mode preserves all parentheses around binary operations, with no exception. Use 'X' as the format spec for this mode. Example:

```python
u = prop('(P & Q) | R')
print(f"{u:X}")  # prints '(P & Q) | R'
v = prop('P & Q & R')
print(f"{v:X}")  # prints '((P & Q) & R)'
v = prop('P & (Q & R)')
print(f"{v:X}")  # prints '(P & (Q & R))'
```

Here is a table for some differences between the different modes:

| Simple         | Explicit         |
| -------------- | ---------------- |
| `P`            | `P`              |
| `~~P`          | `~~P`            |
| `P & Q`        | `(P & Q)`        |
| `(P & Q) -> R` | `((P & Q) -> R)` |
| `P & Q & R`    | `((P & Q) & R)`  |

You can also use `format` to use a mode. This can be useful for dynamically choosing a mode.

```python
u = prop('(P & Q) | R')
print(format(u, ''))   # (P & Q) | R
print(format(u, 'S'))  # (P & Q) | R
print(format(u, 'X'))  # ((P & Q) | R)
mode = 'X'
print(format(u, mode))  # ((P & Q) | R)
```

## More Information

For a more in-depth explanation of the classical-logic and its content, see the [Reference](./reference.md).
