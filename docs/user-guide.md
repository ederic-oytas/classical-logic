
# User Guide

## Installation

Install the package using Pip:

```bash
pip install classical-logic
```

## Creating Propositions with `prop()`

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

## Decomposing Propositions

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

This package also supports unpacking. For example:

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

TODO finish

## Formatting

TODO finish
