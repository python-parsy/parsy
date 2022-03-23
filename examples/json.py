from parsy import forward_declaration, regex, seq, string

whitespace = regex(r"\s*")
lexeme = lambda p: p << whitespace
lbrace = lexeme(string("{"))
rbrace = lexeme(string("}"))
lbrack = lexeme(string("["))
rbrack = lexeme(string("]"))
colon = lexeme(string(":"))
comma = lexeme(string(","))
true = lexeme(string("true")).result(True)
false = lexeme(string("false")).result(False)
null = lexeme(string("null")).result(None)
number = lexeme(regex(r"-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?")).map(float)
string_part = regex(r'[^"\\]+')
string_esc = string("\\") >> (
    string("\\")
    | string("/")
    | string('"')
    | string("b").result("\b")
    | string("f").result("\f")
    | string("n").result("\n")
    | string("r").result("\r")
    | string("t").result("\t")
    | regex(r"u[0-9a-fA-F]{4}").map(lambda s: chr(int(s[1:], 16)))
)
quoted = lexeme(string('"') >> (string_part | string_esc).many().concat() << string('"'))

object_pair = forward_declaration()
array = forward_declaration()
json_object = lbrace >> object_pair.sep_by(comma).map(dict) << rbrace
value = quoted | number | json_object | array | true | false | null
array.become(lbrack >> value.sep_by(comma) << rbrack)
object_pair.become(seq(quoted << colon, value).map(tuple))
json = whitespace >> value


def test():
    assert json.parse(
        r"""
    {
        "int": 1,
        "string": "hello",
        "a list": [1, 2, 3],
        "escapes": "\n",
        "nested": {"x": "y"}
    }
"""
    ) == {
        "int": 1,
        "string": "hello",
        "a list": [1, 2, 3],
        "escapes": "\n",
        "nested": {"x": "y"},
    }


if __name__ == "__main__":
    from sys import stdin

    print(repr(json.parse(stdin.read())))
