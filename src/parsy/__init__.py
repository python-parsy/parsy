# -*- coding: utf-8 -*- #

import re
from .version import __version__
from functools import wraps

class ParseError(RuntimeError):
    pass

class Parser(object):
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, stream, index, on_success, on_failure):
        return self.fn(stream, index, on_success, on_failure)

    def parse(self, string):
        (result, _) = (self << eof).parse_partial(string)
        return result

    def parse_partial(self, string):
        # this success function will be tail-called, so its
        # return value will come out of this function
        def success(index, result):
            return (result, string[index:])

        def failure(index, expected):
            raise ParseError('expected '+repr(expected)+' at '+repr(index))

        return self(string, 0, success, failure)

    def bind(self, bind_fn):
        @Parser
        def bound_parser(stream, index, on_success, on_failure):
            def success(new_index, result):
                next_parser = bind_fn(result)
                return next_parser(stream, new_index, on_success, on_failure)

            return self(stream, index, success, on_failure)

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
        def many_parser(stream, index, on_success, on_failure):
            aggregate = []
            def success(new_index, res):
                nonlocal index
                index = new_index
                aggregate.append(res)
                return True

            def failure(new_index, message):
                return False

            while self(stream, index, success, failure):
                pass

            return on_success(index, aggregate)

        return many_parser

    def times(self, min, max=None):
        if max is None:
            max = min

        @Parser
        def times_parser(stream, index, on_success, on_failure):
            aggregate = []
            fail_message = None

            def success(new_index, res):
                nonlocal index
                index = new_index
                aggregate.append(res)
                return True

            def first_failure(new_index, msg):
                nonlocal index
                nonlocal fail_message
                index = new_index
                fail_message = msg
                return False

            def second_failure(new_index, msg):
                return False

            for times in range(0, min):
                result = self(stream, index, success, first_failure)
                if not result:
                    return on_failure(index, fail_message)

            for times in range(min, max):
                result = self(stream, index, success, second_failure)
                if not result:
                    break

            return on_success(index, aggregate)

        return times_parser

    def at_most(self, n):
        return self.times(0, n)

    def at_least(self, n):
        @chain
        def at_least_parser():
            start = yield self.times(n)
            end = yield self.many()
            return start + end

        return at_least_parser

    def __or__(self, other):
        if not isinstance(other, Parser):
            raise TypeError('%s is not a parser!' % repr(Parser))

        @Parser
        def or_parser(stream, index, on_success, on_failure):
            def failure(new_index, message):
                # we use the closured index here so it backtracks
                return other(stream, index, on_success, on_failure)

            return self(stream, index, on_success, failure)

        return or_parser

    # haskelley operators, for fun #

    # >>
    def __rshift__(self, other):
        return self.then(other)

    # <<
    def __lshift__(self, other):
        return self.skip(other)

# combinator syntax
def chain(fn):
    def genparser():
        iterator = fn()

        def send(val):
            try:
                next_parser = iterator.send(val)
                return next_parser.bind(send)
            except StopIteration as result:
                if isinstance(result.value, Parser):
                    return result.value

                return success(result.value)

        return send(None)

    # this makes sure there is a separate instance of the generator
    # for each parse
    @wraps(fn)
    @Parser
    def chained(*args):
        return genparser()(*args)

    return chained

def success(val):
    @Parser
    def success_parser(stream, index, on_success, on_failure):
        return on_success(index, val)

    return success_parser

def string(s):
    slen = len(s)

    @Parser
    def string_parser(stream, index, on_success, on_failure):
        if stream[index:index+slen] == s:
            return on_success(index+slen, s)
        else:
            return on_failure(stream, s)

    string_parser.__name__ = 'string_parser<%s>' % s

    return string_parser

def regex(exp, flags=0):
    if isinstance(exp, str):
        exp = re.compile(exp, flags)

    @Parser
    def regex_parser(stream, index, on_success, on_failure):
        match = exp.match(stream, index)
        if match:
            return on_success(match.end(), match.group(0))
        else:
            return on_failure(index, exp.pattern)

    regex_parser.__name__ = 'regex_parser<%s>' % exp.pattern

    return regex_parser

whitespace = regex(r'\s+')

@Parser
def eof(stream, index, on_success, on_failure):
    if index < len(stream):
        return on_failure(index, 'EOF')

    return on_success(index, None)
