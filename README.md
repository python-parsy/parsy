# parsy

Parsy is an easy way to combine simple, small parsers into complex, larger parsers.  If it means anything to you, it's a monadic parser combinator library in the spirit of Parsec, Parsnip, and Parsimmon.

Parsy requires python 3.3 or greater.

## Usage

### Simple parser generators

* `string(expected_string)`

    Returns a parser that expects the `expected_string` and produces
    that string value.

* `regex(exp, [flags=0])`

    Returns a parser that expects the given `exp`, and produces the
    matched string.  `exp` can be a compiled regular expression, or a
    string which will be compiled with the given `flags`.

* `success(val)`

    Returns a parser that does not consume any of the stream, but produces
    `val`.

### Parser methods

* `parser.parse(string)`

    Attempts to parse the given `string`.  If the parse is successful and
    consumes the entire string, the result is returned - otherwise, a
    `ParseError` is raised.

* `parser.parse_partial(string)`

    Similar to `parse`, except that it does not require the entire string
    to be consumed.  Returns a tuple of `(result, rest_of_string)`, where
    `rest_of_string` is the part of the string that was left over.

* `parser | other_parser`

    Returns a parser that tries `parser` and, if it fails, backtracks and
    tries `other_parser`.  These can be chained together.

    The resulting parser will produce the value produced by the first
    successful parser.

``` python
>>> parser = string('x') | string('y') | string('z')
>>> parser.parse('x')
'x'
>>> parser.parse('y')
'y'
>>> parser.parse('z')
'z'
```

* `parser.then(other_parser)` (also `parser >> other_parser`)

    Returns a parser which, if `parser` succeeds, will continue parsing with
    `other_parser`.  This will produce the value produced by `other_parser`

``` python
>>> (string('x') >> string('y')).parse('xy')
'y'
```

* `parser.skip(other_parser)` (also `parser << other_parser`)

    Similar to `then` (or `>>`), except the resulting parser will use the
    value produced by the first parser.

``` python
>>> (string('x') << string('y')).parse('xy')
'x'
```

* `parser.many()`

    Returns a parser that expects `parser` 0 or more times, and produces
    a list of the results.  Note that this parser can never fail -
    only produce an empty list.

``` python
>>> parser = regex(r'[a-z]').many()
>>> parser.parse('')
[]
>>> parser.parse('abc')
['a', 'b', 'c']
```

* `parser.times(min [, max=min])`

    Returns a parser that expects `parser` at least `min` times, and
    at most `max` times, and produces a list of the results.  If only
    one argument is given, the parser is expected exactly that number
    of times.

* `parser.at_most(n)`

    Returns a parser that expects `parser` at most `n` times, and produces
    a list of the results.

* `parser.at_least(n)`

    Returns a parser that expects `parser` at least `n` times, and
    produces a list of the results.

* `parser.map(fn)`

    Returns a parser that transforms the produced value of `parser` with
    `fn`.

``` python
>>> regex(r'[0-9]+').map(int).parse('1234')
1234
```

* `parser.result(val)`

    Returns a parser that always produces `val`.

``` python
>>> string('foo').result(42).parse('foo')
42
```

* `parser.bind(fn)`

    Returns a parser which, if `parser` is successful, passes the result
    to `fn`, and continues with the parser returned from `fn`.  This is
    the monadic binding operation.

### Generating a parser

The most powerful way to construct a parser is to use the `generate`
decorator.  `parsy.generate` decorates a generator that yields parsers.
Each time a parser is yielded, the produced value is returned from that
yield expression.  The generator should then return the intended value
to be produced.  (this feature requires python 3.3 or greater)

``` python
from parsy import generate

@generate
def form():
    """parses an s-expression form, like (a b c)"""
    yield lparen
    exprs = yield expr.many()
    yield rparen
    return exprs
```

Note that there is no guarantee that the entire function is executed:
if any of the yielded parsers fails, parsy will try to backtrack to an
alternative parser.
