from parsy import forward_declaration, regex, seq, string

# Utilities
whitespace = regex(r"\s*")
lexeme = lambda p: p << whitespace

# Punctuation
lbrace = lexeme(string("{"))
rbrace = lexeme(string("}"))
lbrack = lexeme(string("["))
rbrack = lexeme(string("]"))
colon = lexeme(string(":"))
comma = lexeme(string(","))

# Primitives
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

# Data structures
json_value = forward_declaration()
object_pair = seq(quoted << colon, json_value).map(tuple)
json_object = lbrace >> object_pair.sep_by(comma).map(dict) << rbrace
array = lbrack >> json_value.sep_by(comma) << rbrack

# Everything
json_value.become(quoted | number | json_object | array | true | false | null)
json_doc = whitespace >> json_value


def test():
    assert (
        json_doc.parse(
            r"""
    {
        "int": 1,
        "string": "hello",
        "a list": [1, 2, 3],
        "escapes": "\n \u24D2",
        "nested": {"x": "y"},
        "other": [true, false, null]
    }
"""
        )
        == {
            "int": 1,
            "string": "hello",
            "a list": [1, 2, 3],
            "escapes": "\n ⓒ",
            "nested": {"x": "y"},
            "other": [True, False, None],
        }
    )


if __name__ == "__main__":
    from sys import stdin

    print(repr(json_doc.parse(stdin.read())))
