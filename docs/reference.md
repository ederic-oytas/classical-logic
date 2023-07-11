
# API Reference

## Subclasses

There are seven proposition classes in total, with
[`Proposition`][flogic.Proposition] being the base class of all proposition
types. Each subclass is a [dataclass][dataclasses] type, which means instances
can be created and be treated like a regular dataclass type:

```python
import flogic as fl

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

| Class Constructor                        | Operation               |
| ---------------------------------------- | ----------------------- |
| [`And(left, right)`][flogic.And]         | `P & Q`                 |
| [`Iff(left, right)`][flogic.Iff]         | `P <-> Q`               |
| [`Implies(left, right)`][flogic.Implies] | `P -> Q`                |
| [`Not(inner)`][flogic.Not]               | `~P`                    |
| [`Predicate(name)`][flogic.Predicate]    | `P`                     |
| [`Or(left, right)`][flogic.Or]           | <code>P &#124; Q</code> |

----

::: flogic.And

----

::: flogic.Iff

----

::: flogic.Implies

----

::: flogic.Not

----

::: flogic.Predicate

----

::: flogic.Proposition
    options:
      filters:
        - "!^_[^_]"
        - "!__.+__"

----

::: flogic.Or
