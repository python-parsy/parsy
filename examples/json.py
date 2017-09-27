import re
from sys import stdin

from parsy import generate, regex, string

whitespace = regex(r'\s*', re.MULTILINE)

lexeme = lambda p: p << whitespace

lbrace = lexeme(string('{'))
rbrace = lexeme(string('}'))
lbrack = lexeme(string('['))
rbrack = lexeme(string(']'))
colon  = lexeme(string(':'))
comma  = lexeme(string(','))
true   = lexeme(string('true')).result(True)
false  = lexeme(string('false')).result(False)
null   = lexeme(string('null')).result(None)

number = lexeme(
    regex(r'-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')
).map(float)

string_part = regex(r'[^"\\]+')
string_esc = string('\\') >> (
    string('\\')
    | string('/')
    | string('b').result('\b')
    | string('f').result('\f')
    | string('n').result('\n')
    | string('r').result('\r')
    | string('t').result('\t')
    | regex(r'u[0-9a-fA-F]{4}').map(lambda s: chr(int(s[1:], 16)))
)


@lexeme
@generate
def quoted():
    yield string('"')
    body = yield (string_part | string_esc).many()
    yield string('"')
    return ''.join(body)


@generate
def array():
    yield lbrack
    first = yield value
    rest = yield (comma >> value).many()
    yield rbrack
    rest.insert(0, first)
    return rest


@generate
def object_pair():
    key = yield quoted
    yield colon
    val = yield value
    return (key, val)


@generate
def json_object():
    yield lbrace
    first = yield object_pair
    rest = yield (comma >> value).many()
    yield rbrace
    rest.insert(0, first)
    return dict(rest)


value = quoted | number | json_object | array | true | false | null
json = whitespace >> value

if __name__ == '__main__':
    print(repr(json.parse(stdin.read())))
