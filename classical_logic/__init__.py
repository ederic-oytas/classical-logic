"""Python package for propositional logic."""
from .core import (
    And,
    Predicate,
    Not,
    Proposition,
    Or,
    Implies,
    Iff,
    atomics,
)
from .parsing import prop, props
