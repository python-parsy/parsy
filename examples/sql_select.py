# A very limited parser for SQL SELECT statements,
# for demo purposes. Supports:
# 1. A simple list of columns (or number/string literals)
# 2. A simple table name
# 3. An optional where condition,
#    which has the form of 'A op B' where A and B are columns, strings or number,
#    and op is a comparison operator
#
# We demonstrate the use of `map` to create AST nodes with a single arg,
# and `seq` for AST nodes with more than one arg.


import attr

from parsy import regex, seq, string, string_from

# -- AST nodes.


@attr.s
class Number:
    value = attr.ib()


@attr.s
class String:
    value = attr.ib()


@attr.s
class Field:
    name = attr.ib()


@attr.s
class Table:
    name = attr.ib()


@attr.s
class Comparison:
    left = attr.ib()
    operator = attr.ib()
    right = attr.ib()


@attr.s
class Select:
    columns = attr.ib()
    table = attr.ib()
    where = attr.ib()


# -- Parsers

number_literal = regex(r'-?[0-9]+').map(int).map(Number)

# We don't support ' in strings or escaping for simplicity
string_literal = regex(r"'[^']*'").map(lambda s: String(s[1:-1]))

identifier = regex('[a-zA-Z][a-zA-Z0-9_]*')

field = identifier.map(Field)

table = identifier.map(Table)

space = regex(r'\s+')  # non-optional whitespace
padding = regex(r'\s*')  # optional whitespace

column_expr = field | string_literal | number_literal

operator = string_from('=', '<', '>', '<=', '>=')

comparison = seq(
    left=column_expr << padding,
    operator=operator,
    right=padding >> column_expr,
).combine_dict(Comparison)

SELECT = string('SELECT')
FROM = string('FROM')
WHERE = string('WHERE')

# Here we demonstrate use of leading underscore to discard parts we don't want,
# which is more readable and convenient than `<<` and `>>` sometimes.
select = seq(
    _select=SELECT + space,
    columns=column_expr.sep_by(padding + string(',') + padding, min=1),
    _from=space + FROM + space,
    table=table,
    where=(space >> WHERE >> space >> comparison).optional(),
    _end=padding + string(';')
).combine_dict(Select)


def test_select():
    assert select.parse(
        "SELECT thing, stuff, 123, 'hello' FROM my_table WHERE id = 1;"
    ) == Select(
        columns=[Field("thing"), Field("stuff"), Number(123), String("hello")],
        table=Table("my_table"),
        where=Comparison(
            left=Field("id"),
            operator="=",
            right=Number(1)
        )
    )


def test_optional_where():
    assert select.parse(
        "SELECT 1 FROM x;"
    ) == Select(
        columns=[Number(1)],
        table=Table("x"),
        where=None,
    )
