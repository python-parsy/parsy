from parsy import string, regex, generate, ParseError
import pdb

def test_string():
    parser = string('x')
    assert parser.parse('x') == 'x'

    try: parser.parse('y'); assert False
    except ParseError: pass

def test_regex():
    parser = regex(r'[0-9]')

    assert parser.parse('1') == '1'
    assert parser.parse('4') == '4'

    try: parser.parse('x'); assert False
    except ParseError: pass

def test_then():
    xy_parser = string('x') >> string('y')
    assert xy_parser.parse('xy') == 'y'

    try: xy_parser.parse('y'); assert False
    except ParseError: pass

    try: xy_parser.parse('z'); assert False
    except ParseError: pass

def test_bind():
    piped = None

    def binder(x):
        nonlocal piped
        piped = x
        return string('y')

    parser = string('x').bind(binder)

    assert parser.parse('xy') == 'y'
    assert piped == 'x'

    try: parser.parse('x'); assert False
    except ParseError: pass

def test_generate():
    x = y = None
    @generate
    def parser():
        nonlocal x
        nonlocal y
        x = yield string('x')
        y = yield string('y')
        return 3

    assert parser.parse('xy') == 3
    assert x == 'x'
    assert y == 'y'

def test_generate_backtracking():
    @generate
    def xy():
        yield string('x')
        yield string('y')
        assert False

    parser = xy | string('z')
    # should not finish executing xy()
    assert parser.parse('z') == 'z'

def test_or():
    x_or_y = string('x') | string('y')

    assert x_or_y.parse('x') == 'x'
    assert x_or_y.parse('y') == 'y'

def test_or_with_then():
    parser = (string('\\') >> string('y')) | string('z')
    assert parser.parse('\\y') == 'y'
    assert parser.parse('z') == 'z'

    try: parser.parse('\\z'); assert False
    except ParseError: pass

def test_many():
    letters = letter.many()
    assert letters.parse('x') == ['x']
    assert letters.parse('xyz') == ['x', 'y', 'z']
    assert letters.parse('') == []

    try: letters.parse('1'); assert False
    except ParseError: pass

def test_many_with_then():
    parser = string('x').many() >> string('y')
    assert parser.parse('y') == 'y'
    assert parser.parse('xy') == 'y'
    assert parser.parse('xxxxxy') == 'y'

def test_times_zero():
    zero_letters = letter.times(0)
    assert zero_letters.parse('') == []

    try: zero_letters.parse('x'); assert False
    except ParseError: pass

def test_times():
    three_letters = letter.times(3)
    assert three_letters.parse('xyz') == ['x', 'y', 'z']

    try: three_letters.parse('xy'); assert False
    except ParseError: pass

    try: three_letters.parse('xyzw'); assert False
    except ParseError: pass

def test_times_with_then():
    then_digit = letter.times(3) >> digit
    assert then_digit.parse('xyz1') == '1'

    try: then_digit.parse('xy1'); assert False
    except ParseError: pass

    try: then_digit.parse('xyz'); assert False
    except ParseError: pass

    try: then_digit.parse('xyzw'); assert False
    except ParseError: pass

def test_times_with_min_and_max():
    some_letters = letter.times(2, 4)

    assert some_letters.parse('xy') == ['x', 'y']
    assert some_letters.parse('xyz') == ['x', 'y', 'z']
    assert some_letters.parse('xyzw') == ['x', 'y', 'z', 'w']

    try: some_letters.parse('x'); assert False
    except ParseError: pass

    try: some_letters.parse('xyzwv'); assert False
    except ParseError: pass

def test_times_with_min_and_max_and_then():
    then_digit = letter.times(2, 4) >> digit

    assert then_digit.parse('xy1') == '1'
    assert then_digit.parse('xyz1') == '1'
    assert then_digit.parse('xyzw1') == '1'

    try: then_digit.parse('xy'); assert False
    except ParseError: pass

    try: then_digit.parse('xyzw'); assert False
    except ParseError: pass

    try: then_digit.parse('xyzwv1'); assert False
    except ParseError: pass

    try: then_digit.parse('x1'); assert False
    except ParseError: pass
