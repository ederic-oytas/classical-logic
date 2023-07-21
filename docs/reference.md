
# API Reference

## Subclasses

There are seven proposition classes in total, with
[`Proposition`][classical_logic.Proposition] being the base class of all proposition
types. Each subclass is a [dataclass][dataclasses] type, which means instances
can be created and be treated like a regular dataclass type:

```python
import classical_logic as fl

u = fl.And(fl.Predicate('P'), fl.Predicate('Q'))
assert u == fl.prop('P & Q')
assert u.left == prop('P')
assert u.right == prop('Q')

v = fl.Or(left=fl.Predicate(name='P'), right=fl.Predicate(name='Q'))
assert v == fl.prop('P | Q')
assert v.left == prop('P')
assert v.right == prop('Q')

w = fl.Not(fl.Predicate('P'))
assert w == fl.prop('~P')
assert w.inner == fl.prop('P')
assert w.inner.name == 'P'
```

The following table gives the subclass constructors and the operation it
corresponds to:

| Class Constructor                                 | Operation               |
| ------------------------------------------------- | ----------------------- |
| [`And(left, right)`][classical_logic.And]         | `P & Q`                 |
| [`Iff(left, right)`][classical_logic.Iff]         | `P <-> Q`               |
| [`Implies(left, right)`][classical_logic.Implies] | `P -> Q`                |
| [`Not(inner)`][classical_logic.Not]               | `~P`                    |
| [`Predicate(name)`][classical_logic.Predicate]    | `P`                     |
| [`Or(left, right)`][classical_logic.Or]           | <code>P &#124; Q</code> |

----

::: classical_logic.And

----

::: classical_logic.Iff

----

::: classical_logic.Implies

----

::: classical_logic.Not

----

::: classical_logic.Predicate

----

::: classical_logic.Proposition
    options:
      filters:
        - "!^_[^_]"
        - "!__.+__"

----

::: classical_logic.Or

----

::: classical_logic.prop

----

::: classical_logic.props
