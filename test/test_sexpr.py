import re
import unittest

from parsy import generate, regex, string

whitespace = regex(r'\s+', re.MULTILINE)
comment = regex(r';.*')
ignore = (whitespace | comment).many()

lexeme = lambda p: p << ignore

lparen = lexeme(string('('))
rparen = lexeme(string(')'))
number = lexeme(regex(r'\d+')).map(int)
symbol = lexeme(regex(r'[\d\w_-]+'))
true   = lexeme(string('#t')).result(True)
false  = lexeme(string('#f')).result(False)

atom = true | false | number | symbol


@generate('a form')
def form():
    yield lparen
    els = yield expr.many()
    yield rparen
    return els


@generate
def quote():
    yield string("'")
    e = yield expr
    return ['quote', e]


expr = form | quote | atom
program = ignore >> expr.many()


class TestSexpr(unittest.TestCase):
    def test_form(self):
        result = program.parse('(1 2 3)')
        self.assertEqual(result, [[1, 2, 3]])

    def test_quote(self):
        result = program.parse("'foo '(bar baz)")
        self.assertEqual(result,
                         [['quote', 'foo'], ['quote', ['bar', 'baz']]])

    def test_double_quote(self):
        result = program.parse("''foo")
        self.assertEqual(result, [['quote', ['quote', 'foo']]])

    def test_boolean(self):
        result = program.parse('#t #f')
        self.assertEqual(result, [True, False])

    def test_comments(self):
        result = program.parse(
            """
            ; a program with a comment
            (           foo ; that's a foo
            bar )
            ; some comments at the end
            """
        )

        self.assertEqual(result, [['foo', 'bar']])


if __name__ == '__main__':
    unittest.main()
