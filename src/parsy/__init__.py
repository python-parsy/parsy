# -*- coding: utf-8 -*- #

import re
from .version import __version__  # noqa: F401
from functools import wraps
from collections import namedtuple


def line_info_at(stream, index):
    if index > len(stream):
        raise ValueError("invalid index")
    line = stream.count("\n", 0, index)
    last_nl = stream.rfind("\n", 0, index)
    col = index - (last_nl + 1)
    return (line, col)


class ParseError(RuntimeError):
    def __init__(self, expected, stream, index):
        self.expected = expected
        self.stream = stream
        self.index = index

    def line_info(self):
        try:
            return '{}:{}'.format(*line_info_at(self.stream, self.index))
        except ValueError:
            return '<out of bounds index {!r}>'.format(self.index)

    def __str__(self):
        return 'expected {} at {}'.format(self.expected, self.line_info())


class Result(namedtuple('Result', 'status index value furthest expected')):
    @staticmethod
    def success(index, value):
        return Result(True, index, value, -1, None)

    @staticmethod
    def failure(index, expected):
        return Result(False, -1, None, index, expected)

    # collect the furthest failure from self and other
    def aggregate(self, other):
        if not other:
            return self
        if self.furthest >= other.furthest:
            return self

        return Result(self.status, self.index, self.value, other.furthest, other.expected)


class Parser(object):
    """
    A Parser is an object that wraps a function whose arguments are
    a string to be parsed and the index on which to begin parsing.
    The function should return either Result.success(next_index, value),
    where the next index is where to continue the parse and the value is
    the yielded value, or Result.failure(index, expected), where expected
    is a string indicating what was expected, and the index is the index
    of the failure.
    """

    def __init__(self, wrapped_fn):
        self.wrapped_fn = wrapped_fn

    def __call__(self, stream, index):
        return self.wrapped_fn(stream, index)

    def parse(self, string):
        """Parse a string and return the result or raise a ParseError."""
        (result, _) = (self << eof).parse_partial(string)
        return result

    def parse_partial(self, string):
        """
        Parse the longest possible prefix of a given string.
        Return a tuple of the result and the rest of the string,
        or raise a ParseError.
        """
        if not isinstance(string, str):
            raise TypeError('parsy can only parse strings! got {!r}'.format(string))

        result = self(string, 0)

        if result.status:
            return (result.value, string[result.index:])
        else:
            raise ParseError(result.expected, string, result.furthest)

    def bind(self, bind_fn):
        @Parser
        def bound_parser(stream, index):
            result = self(stream, index)

            if result.status:
                next_parser = bind_fn(result.value)
                return next_parser(stream, result.index).aggregate(result)
            else:
                return result

        return bound_parser

    def map(self, map_fn):
        return self.bind(lambda res: success(map_fn(res)))

    def then(self, other):
        return seq(self, other).map(lambda r: r[1])

    def skip(self, other):
        return seq(self, other).map(lambda r: r[0])

    def result(self, res):
        return self >> success(res)

    def many(self):
        return self.times(0, float('inf'))

    def times(self, min, max=None):
        # max=None means exactly min
        # min=max=None means from 0 to infinity
        if max is None:
            max = min

        @Parser
        def times_parser(stream, index):
            values = []
            times = 0
            result = None

            while times < max:
                result = self(stream, index).aggregate(result)
                if result.status:
                    values.append(result.value)
                    index = result.index
                    times += 1
                elif times >= min:
                    break
                else:
                    return result

            return Result.success(index, values).aggregate(result)

        return times_parser

    def at_most(self, n):
        return self.times(0, n)

    def at_least(self, n):
        return self.times(n) + self.many()

    def desc(self, description):
        return self | fail(description)

    def mark(self):
        @generate
        def marked():
            start = yield line_info
            body = yield self
            end = yield line_info
            return (start, body, end)

        return marked

    def __add__(self, other):
        return seq(self, other).map(lambda res: res[0] + res[1])

    def __mul__(self, other):
        if isinstance(other, range):
            return self.times(other.start, other.stop - 1)
        return self.times(other)

    def __or__(self, other):
        if not isinstance(other, Parser):
            raise TypeError('{!r} is not a parser!'.format(other))

        return alt(self, other)

    # haskelley operators, for fun #

    # >>
    def __rshift__(self, other):
        return self.then(other)

    # <<
    def __lshift__(self, other):
        return self.skip(other)


def alt(*parsers):
    if not parsers:
        return fail('<empty alt>')

    @Parser
    def alt_parser(stream, index):
        result = None
        for parser in parsers:
            result = parser(stream, index).aggregate(result)
            if result.status:
                return result

        return result

    return alt_parser


def seq(*parsers):
    """
    Takes a list of list of parsers, runs them in order,
    and collects their individuals results in a list
    """
    if not parsers:
        return success([])

    @Parser
    def seq_parser(stream, index):
        result = None
        values = []
        for parser in parsers:
            result = parser(stream, index).aggregate(result)
            if not result.status:
                return result
            index = result.index
            values.append(result.value)

        return Result.success(index, values).aggregate(result)

    return seq_parser


def seq_map(*args):
    (*parsers, fn) = args
    return seq(*parsers).map(lambda values: fn(*values))


# combinator syntax
def generate(fn):
    if isinstance(fn, str):
        return lambda f: generate(f).desc(fn)

    @wraps(fn)
    @Parser
    def generated(stream, index):
        # start up the generator
        iterator = fn()

        result = None
        value = None
        try:
            while True:
                next_parser = iterator.send(value)
                result = next_parser(stream, index).aggregate(result)
                if not result.status:
                    return result
                value = result.value
                index = result.index
        except StopIteration as stop:
            returnVal = stop.value
            if isinstance(returnVal, Parser):
                return returnVal(stream, index).aggregate(result)

            return Result.success(index, returnVal).aggregate(result)

    return generated.desc(fn.__name__)


index = Parser(lambda _, index: Result.success(index, index))
line_info = Parser(lambda stream, index: Result.success(index, line_info_at(stream, index)))


def success(val):
    return Parser(lambda _, index: Result.success(index, val))


def fail(expected):
    return Parser(lambda _, index: Result.failure(index, expected))


def string(s):
    slen = len(s)

    @Parser
    def string_parser(stream, index):
        if stream[index:index + slen] == s:
            return Result.success(index + slen, s)
        else:
            return Result.failure(index, s)

    string_parser.__name__ = 'string_parser<%s>' % s

    return string_parser


def regex(exp, flags=0):
    if isinstance(exp, str):
        exp = re.compile(exp, flags)

    @Parser
    def regex_parser(stream, index):
        match = exp.match(stream, index)
        if match:
            return Result.success(match.end(), match.group(0))
        else:
            return Result.failure(index, exp.pattern)

    regex_parser.__name__ = 'regex_parser<%s>' % exp.pattern

    return regex_parser


whitespace = regex(r'\s+')


@Parser
def letter(stream, index):
    if index < len(stream) and stream[index].isalpha():
        return Result.success(index + 1, stream[index])
    else:
        return Result.failure(index, 'a letter')


@Parser
def digit(stream, index):
    if index < len(stream) and stream[index].isdigit():
        return Result.success(index + 1, stream[index])
    else:
        return Result.failure(index, 'a digit')


@Parser
def eof(stream, index):
    if index >= len(stream):
        return Result.success(index, None)
    else:
        return Result.failure(index, 'EOF')
