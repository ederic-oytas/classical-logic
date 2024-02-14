
# classical-logic - Tools for Classical Logic

<a href='https://classical-logic.readthedocs.io/en/stable/?badge=stable'>
    <img src='https://readthedocs.org/projects/classical-logic/badge/?version=stable' alt='Documentation Status' />
</a>
<a href="https://github.com/ederic-oytas/classical-logic/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/ederic-oytas/classical-logic"></a>

`classical-logic` is a Python package that allows you to work with logical
propositions as Python objects.

It's extremely simple to use:

```python
from classical_logic import prop

p = prop('P & Q')
assert p(P=True, Q=True) is True
assert p(P=True, Q=False) is False
```

## Features

Parse proposition objects:

```python
from classical_logic import prop

# Can parse simple propositions:
p = prop('P | Q')
# As well as complex ones!
p = prop('P & (Q | (Q -> R)) <-> S')
```

Compose proposition objects:

```python
p = prop('P')
q = prop('Q')

# Create conjunctions and disjunctions with & and |:
u = p & (q | p)   # P & (Q | P)

# Create conditionals and biconditionals as well:
u = p.implies(q)  # P -> Q
u = p.iff(q)      # P <-> Q
```

Decompose propositions:

```python
u = prop('P & Q')

# Use indexing to 
assert u[0] == prop('P')
assert u[1] == prop('Q')

# You can also use Python's unpacking feature!
p, q = u
assert p == prop('P')
assert q == prop('Q')
```

Interpret propositions (assign truth values):

```python
u = prop('P <-> Q')

# Call the proposition like a function to interpret it
assert u(P=True, Q=True) is True
assert u(P=True, Q=False) is False
assert u(P=False, Q=False) is True
```

**No dependencies.** This package doesn't use any dependencies.

Want to use this package? See the [documentation](
https://classical-logic.readthedocs.io/en/stable/)!

## Links

[Documentation @ ReadTheDocs](
https://classical-logic.readthedocs.io/en/stable/)

[Github Repository](https://github.com/ederic-oytas/classical-logic)

[PyPI Page](https://pypi.org/project/classical-logic/)

## Installation

This package can be installed using Pip:

```bash
pip install classical-logic
```

Please make sure you use a dash (-) instead of an underscore (_).

## Bug Reports and Feature Requests

You can report a bug or suggest a feature on the Github repo.

See the [Issues page on Github](
https://github.com/ederic-oytas/classical-logic/issues/new/choose).

## Contributions

Contributions to this project are welcome. :)

See the [pull requests page on Github](
https://github.com/ederic-oytas/classical-logic/pulls).
