
# API Reference

## Subclasses

There are seven proposition classes in total, with
[`Proposition`][classical_logic.Proposition] being the base class of all proposition
types. Each subclass is a [dataclass][dataclasses] type, which means instances
can be created and be treated like a regular dataclass type:

```python
import classical_logic as cl

u = cl.And(cl.Predicate('P'), cl.Predicate('Q'))
assert u == cl.prop('P & Q')
assert u.left == cl.prop('P')
assert u.right == cl.prop('Q')

v = cl.Or(left=cl.Predicate(name='P'), right=cl.Predicate(name='Q'))
assert v == cl.prop('P | Q')
assert v.left == cl.prop('P')
assert v.right == cl.prop('Q')

w = cl.Not(cl.Predicate('P'))
assert w == cl.prop('~P')
assert w.inner == cl.prop('P')
assert w.inner.name == 'P'
```

The following table gives the subclass constructors and the proposition it
corresponds to:

| Class Constructor                                 | Proposition             |
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
