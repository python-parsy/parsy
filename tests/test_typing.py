# Attempt to add type annotations to Parsy.
#
# In the simplest case, a type checker could check that we are using only
# methods that exist on `Parser` instances, like `parse` and `parse_partial`.
# That's not hugely useful, however.
#
# In reality, `Parser` instances are generic in what they produce.
# (We'll ignore polymorphism in input type, and assume we only consume `str`)
#
# For example, `string("xxx")` is a `Parser` whose `parse` method will produce
# a `str`.
# However, `string("123").map(int)` is a `Parser` whose `parse` method will produce
# an `int`.
#
# `string("123").map(int) << string(",")` also produces `int`

# With appropriate type definitions on `map`, `__lshift__` etc. methods, we can
# get this to work:

from dataclasses import dataclass

import parsy


@dataclass
class Foo:
    val: int


# mypy correctly accepts these:
good_type: str = parsy.string("test").parse("test")
good_type2: int = parsy.string("123").map(int).parse("123")
good_type3: Foo = (parsy.regex(r"\d+").map(int).map(Foo) << parsy.string("x")).parse("123x")

# and it correctly rejects these, with sensible error messages:
bad_type: int = parsy.string("test").parse("test")
bad_type2: int = parsy.string("test").map(str).parse("test")
bad_type3: str = parsy.string("123").map(int).parse("123")
bad_type4: Foo = (parsy.regex(r"\d+").map(int).map(Foo) >> parsy.string("x")).parse("123x")

# However, once we come to `seq`, `alt`, `Parser.combine` and
# `Parser.combine_dict`, things get much more difficult:


@dataclass
class Pair:
    key: str
    val: int


pair = parsy.seq(
    key=parsy.regex("[a-z]+"),
    _eq=parsy.string("="),
    val=parsy.regex(r"\d+").map(int),
).combine_dict(Pair)

good_type4: Pair = pair.parse("x=123")

# Getting the following to be rejected is a challenge!
bad_type5: Foo = pair.parse("x=123")  # should be Pair not Food

bad_pair = parsy.seq(
    key=parsy.regex("[a-z]+"),
    _eq=parsy.string("="),
    val=parsy.regex(r"\d+"),  # this is missing a `map(int)`, incompatible with Pair.val should be rejected.
).combine_dict(Pair)


# The following works, but creates a Pair with `val` as `str` which shouldn't be allowed.
bad_type6: Pair = bad_pair.parse("x=123")


# We have other issues, like forward_declaration which kind of breaks everything
# because you don't know what type it is until later.
