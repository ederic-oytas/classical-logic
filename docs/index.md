
# `classical-logic` - Tools for Classical Logic.

This package makes it easy to work with propositions in classical logic.

Here is an example:

```python
import classical_logic as cl


p = cl.prop('(P & Q) | ~R')
assert p(P=True, Q=True, R=True) is True
assert p(P=False, Q=False, R=True) is False
```

Features:

- Proposition objects.
- Parser for classical logic.

## Links

[Github Repository](https://github.com/ederic-oytas/python-freezable)

[PyPI Page](https://pypi.org/project/classical-logic/)

## Installation

This package can be installed using Pip:

```bash
pip install classical-logic
```

Please make sure you use a dash (-) instead of an underscore (_).

## Bug Reports and Feature Requests.

You can report a bug or suggest a feature on the Github repo.

See the [Issues page on Github](
https://github.com/ederic-oytas/classical-logic/issues/new/choose).

## Contributions

Contributions to this project are welcome. :)

See the [pull requests page on Github](
https://github.com/ederic-oytas/classical-logic/pulls).
