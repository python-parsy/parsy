# -*- coding: utf-8 -*- #

import re
from .version import __version__
from functools import wraps
from collections import namedtuple

class ParseError(RuntimeError):
    pass

Result = namedtuple('Result', ['success', 'index', 'value'])

class Parser(object):
    """
    A Parser is an object that wraps a function whose arguments are
    a string to be parsed and the index on which to begin parsing.
    The function returns a 3-tuple of (status, next_index, value),
    where the status is True if the parse was successful and False
    otherwise, the next_index is where to begin the next parse
    (or where to report a failure), and the value is the yielded value
    (or an error message).
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
        (status, index, value) = self(string, 0)

        if status:
            return (value, string[index:])
        else:
            raise ParseError('expected {!r} at {!r}'.format(value, index))

    def bind(self, bind_fn):
        @Parser
        def bound_parser(stream, index):
            def success(new_index, result):
                next_parser = bind_fn(result)
                return next_parser(stream, new_index)

            (success, new_index, value) = self(stream, index)

            if success:
                next_parser = bind_fn(value)
                return next_parser(stream, new_index)
            else:
                return (False, index, value)

        return bound_parser

    def map(self, map_fn):
        return self.bind(lambda res: success(map_fn(res)))

    def then(self, other):
        return self.bind(lambda _: other)

    def skip(self, other):
        return self.bind(lambda res: other.result(res))

    def result(self, res):
        return self >> success(res)

    def many(self):
        @Parser
        def many_parser(stream, index):
            aggregate = []
            next_index = index

            while True:
                (status, next_index, value) = self(stream, index)
                if status:
                    aggregate.append(value)
                    index = next_index
                else:
                    break

            return (True, index, aggregate)

        return many_parser

    def times(self, min, max=None):
        if max is None:
            max = min

        @Parser
        def times_parser(stream, index):
            aggregate = []
            next_index = index

            for times in range(0, min):
                (status, next_index, value) = self(stream, index)
                index = next_index
                if status:
                    aggregate.append(value)
                else:
                    return (False, index, value)

            for times in range(min, max):
                (status, next_index, value) = self(stream, index)
                if status:
                    index = next_index
                    aggregate.append(value)
                else:
                    break

            return (True, index, aggregate)

        return times_parser

    def at_most(self, n):
        return self.times(0, n)

    def at_least(self, n):
        @generate
        def at_least_parser():
            start = yield self.times(n)
            end = yield self.many()
            return start + end

        return at_least_parser

    def __or__(self, other):
        if not isinstance(other, Parser):
            raise TypeError('{!r} is not a parser!'.format(other))

        @Parser
        def or_parser(stream, index):
            def failure(new_index, message):
                # we use the closured index here so it backtracks
                return other(stream, index)

            (status, next_index, value) = self(stream, index)
            if status:
                return (True, next_index, value)
            else:
                return other(stream, index)

        return or_parser

    # haskelley operators, for fun #

    # >>
    def __rshift__(self, other):
        return self.then(other)

    # <<
    def __lshift__(self, other):
        return self.skip(other)

# combinator syntax
def generate(fn):
    @wraps(fn)
    @Parser
    def generated(stream, index):
        iterator = fn()
        value = None
        try:
            while True:
                next_parser = iterator.send(value)
                (status, index, value) = next_parser(stream, index)
                if not status:
                    return (False, index, value)
        except StopIteration as result:
            returnVal = result.value
            if isinstance(returnVal, Parser):
                return returnVal(stream, index)

            return (True, index, returnVal)

    return generated

def success(val):
    @Parser
    def success_parser(stream, index):
        return (True, index, val)

    return success_parser

def string(s):
    slen = len(s)

    @Parser
    def string_parser(stream, index):
        if stream[index:index+slen] == s:
            return (True, index+slen, s)
        else:
            return (False, index, s)

    string_parser.__name__ = 'string_parser<%s>' % s

    return string_parser

def regex(exp, flags=0):
    if isinstance(exp, str):
        exp = re.compile(exp, flags)

    @Parser
    def regex_parser(stream, index):
        match = exp.match(stream, index)
        if match:
            return (True, match.end(), match.group(0))
        else:
            return (False, index, exp.pattern)

    regex_parser.__name__ = 'regex_parser<%s>' % exp.pattern

    return regex_parser

whitespace = regex(r'\s+')

@Parser
def eof(stream, index):
    if index < len(stream):
        return (False, index, 'EOF')

    return (True, index, None)
