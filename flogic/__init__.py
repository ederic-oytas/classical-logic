"""Python package for propositional logic."""
from .core import (
    And,
    Atomic,
    Not,
    Proposition,
    Or,
    Implies,
    Iff,
    UnaryConnection,
    BinaryConnection,
    atomics,
)
from .parsing import prop, props
