from parsy import *

match_one = lambda i1: item_matcher(lambda i2: i1 == i2)

def lexer(code):
    whitespace = regex(r'\s*')
    integer = digit.at_least(1).map(''.join).map(int)
    float_ = (
        digit.many() + string('.').result(['.']) + digit.many()
        ).map(''.join).map(float)
    parser = whitespace >> ((
        integer | float_ | regex(r'[()*/+-]')
        ) << whitespace).many()
    return parser.parse(code)

def syntactic_analysis(tokens):
    lparen = match_one('(')
    rparen = match_one(')')

    @generate
    def additive():
        res = yield multiplicative
        sign = match_one('+') | match_one('-')
        while True:
            operation = yield sign|success('')
            if not operation:
                break
            operand = yield multiplicative
            if operation == '+':
                res += operand
            elif operation == '-':
                res -= operand
        return res

    @generate
    def multiplicative():
        res = yield simple
        sign = match_one('*') | match_one('/')
        while True:
            operation = yield sign|success('')
            if not operation:
                break
            operand = yield simple
            if operation == '*':
                res *= operand
            elif operation == '/':
                res /= operand
        return res

    @generate
    def number():
        sign = yield match_one('+') | match_one('-') | success('+')
        value = yield item_matcher(
            lambda x: isinstance(x, (int, float)), 'number')
        return value if sign == '+' else -value

    expr = additive
    simple = (lparen >> expr << rparen) | number

    return expr.parse(tokens)

def simple_eval(expr):
    return syntactic_analysis(lexer(expr))

if __name__ == '__main__':
    print(simple_eval(input()))
