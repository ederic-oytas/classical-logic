"""Python package for propositional logic."""
from .core import (
    And,
    Predicate,
    Not,
    Proposition,
    Or,
    Implies,
    Iff,
    _Operation1,
    _Operation2,
    atomics,
)
from .parsing import prop, props
