# -*- coding: utf-8 -*- #

import re
from .version import __version__

class ParseError(RuntimeError):
    pass

class Parser(object):
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, stream, index, on_success, on_failure):
        return self.fn(stream, index, on_success, on_failure)

    def parse(self, string):
        # tail-call the identity function so that the
        # result comes out
        success = lambda _, result: result

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
        return self.then(success(res))

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

    def times(self):
        raise 'TODO'

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

    # >>=
    def __irshift__(self, bind_fn):
        return self.bind(bind_fn)

    # >>
    def __rshift__(self, other):
        return self.then(other)

    # <<
    def __lshift__(self, other):
        return self.skip(other)

# combinator syntax
def combine(fn):
    def genparser():
        iterator = fn()

        def send(val):
            try:
                next_parser = iterator.send(val)
                return next_parser.bind(lambda result: send(result))
            except StopIteration as result:
                if isinstance(result.value, Parser):
                    return result.value

                return success(result.value)

        return send(None)

    return success(None).bind(lambda _: genparser())

def success(val):
    @Parser
    def success_parser(stream, index, on_success, on_failure):
        return on_success(index, val)

    return success_parser

def string(s):
    slen = len(s)

    @Parser
    def string_parser(stream, index, on_success, on_failure):
        if s == stream[index:index+slen] == s:
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
