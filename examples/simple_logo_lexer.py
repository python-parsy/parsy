"""
Stripped down logo lexer, for tokenizing Turtle Logo programs like:

   fd 1
   bk 2
   rt 90

etc.
"""

from parsy import eof, regex, seq, string, string_from, whitespace

command = string_from("fd", "bk", "rt", "lt")
number = regex(r'[0-9]+').map(int)
optional_whitespace = regex(r'\s*')
eol = string("\n")
line = seq(optional_whitespace >> command,
           whitespace >> number,
           (eof | eol | (whitespace >> eol)).result("\n"))
flatten_list = lambda ls: sum(ls, [])
lexer = line.many().map(flatten_list)
