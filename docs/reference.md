
# API Reference

## Subclasses

There are seven proposition classes in total, with
[`Proposition`][classical-logic.Proposition] being the base class of all proposition
types. Each subclass is a [dataclass][dataclasses] type, which means instances
can be created and be treated like a regular dataclass type:

```python
import classical-logic as fl

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

::: classical-logic.And

----

::: classical-logic.Iff

----

::: classical-logic.Implies

----

::: classical-logic.Not

----

::: classical-logic.Predicate

----

::: classical-logic.Proposition
    options:
      filters:
        - "!^_[^_]"
        - "!__.+__"

----

::: classical-logic.Or

----

::: classical-logic.prop

----

::: classical-logic.props
