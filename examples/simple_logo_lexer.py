"""
Stripped down logo lexer, for tokenizing Turtle Logo programs like:

   fd 1
   bk 2
   rt 90

etc.
"""

from parsy import string, string_from, regex, whitespace, generate, eof

command = string_from("fd", "bk", "rt", "lt")
number = regex(r'[0-9]+').map(int)
optional_whitespace = regex(r'\s*')
eol = string("\n")


@generate
def line():
    yield optional_whitespace
    c = yield command
    yield whitespace
    n = yield number
    yield eof | eol | (whitespace >> eol)
    return [c, n, "\n"]


flatten_list = lambda ls: sum(ls, [])
lexer = line.many().map(flatten_list)
