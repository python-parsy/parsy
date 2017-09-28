import unittest

from parsy import ParseError, digit, generate, letter, regex, seq, string


class TestParser(unittest.TestCase):

    def test_string(self):
        parser = string('x')
        self.assertEqual(parser.parse('x'), 'x')

        self.assertRaises(ParseError, parser.parse, 'y')

    def test_regex(self):
        parser = regex(r'[0-9]')

        self.assertEqual(parser.parse('1'), '1')
        self.assertEqual(parser.parse('4'), '4')

        self.assertRaises(ParseError, parser.parse, 'x')

    def test_then(self):
        xy_parser = string('x') >> string('y')
        self.assertEqual(xy_parser.parse('xy'), 'y')

        self.assertRaises(ParseError, xy_parser.parse, 'y')
        self.assertRaises(ParseError, xy_parser.parse, 'z')

    def test_bind(self):
        piped = None

        def binder(x):
            nonlocal piped
            piped = x
            return string('y')

        parser = string('x').bind(binder)

        self.assertEqual(parser.parse('xy'), 'y')
        self.assertEqual(piped, 'x')

        self.assertRaises(ParseError, parser.parse, 'x')

    def test_map(self):
        parser = digit.map(int)
        self.assertEqual(parser.parse('7'),
                         7)

    def test_combine(self):
        parser = (seq(digit, letter)
                  .combine(lambda d, l: (d, l)))
        self.assertEqual(parser.parse('1A'),
                         ('1', 'A'))

    def test_generate(self):
        x = y = None

        @generate
        def xy():
            nonlocal x
            nonlocal y
            x = yield string('x')
            y = yield string('y')
            return 3

        self.assertEqual(xy.parse('xy'), 3)
        self.assertEqual(x, 'x')
        self.assertEqual(y, 'y')

    def test_mark(self):
        parser = (letter.many().mark() << string("\n")).many()

        lines = parser.parse("asdf\nqwer\n")

        self.assertEqual(len(lines), 2)

        (start, letters, end) = lines[0]
        self.assertEqual(start, (0, 0))
        self.assertEqual(letters, ['a', 's', 'd', 'f'])
        self.assertEqual(end, (0, 4))

        (start, letters, end) = lines[1]
        self.assertEqual(start, (1, 0))
        self.assertEqual(letters, ['q', 'w', 'e', 'r'])
        self.assertEqual(end, (1, 4))

    def test_generate_desc(self):
        @generate('a thing')
        def thing():
            yield string('t')

        with self.assertRaises(ParseError) as err:
            thing.parse('x')

        ex = err.exception

        self.assertEqual(ex.expected, frozenset(['a thing']))
        self.assertEqual(ex.stream, 'x')
        self.assertEqual(ex.index, 0)

    def test_multiple_failures(self):
        abc = string('a') | string('b') | string('c')

        with self.assertRaises(ParseError) as err:
            abc.parse('d')

        ex = err.exception
        self.assertEqual(ex.expected, frozenset(['a', 'b', 'c']))
        self.assertEqual(str(ex), "expected one of 'a', 'b', 'c' at 0:0")

    def test_generate_backtracking(self):
        @generate
        def xy():
            yield string('x')
            yield string('y')
            assert False

        parser = xy | string('z')
        # should not finish executing xy()
        self.assertEqual(parser.parse('z'), 'z')

    def test_or(self):
        x_or_y = string('x') | string('y')

        self.assertEqual(x_or_y.parse('x'), 'x')
        self.assertEqual(x_or_y.parse('y'), 'y')

    def test_or_with_then(self):
        parser = (string('\\') >> string('y')) | string('z')
        self.assertEqual(parser.parse('\\y'), 'y')
        self.assertEqual(parser.parse('z'), 'z')

        self.assertRaises(ParseError, parser.parse, '\\z')

    def test_many(self):
        letters = letter.many()
        self.assertEqual(letters.parse('x'), ['x'])
        self.assertEqual(letters.parse('xyz'), ['x', 'y', 'z'])
        self.assertEqual(letters.parse(''), [])

        self.assertRaises(ParseError, letters.parse, '1')

    def test_many_with_then(self):
        parser = string('x').many() >> string('y')
        self.assertEqual(parser.parse('y'), 'y')
        self.assertEqual(parser.parse('xy'), 'y')
        self.assertEqual(parser.parse('xxxxxy'), 'y')

    def test_times_zero(self):
        zero_letters = letter.times(0)
        self.assertEqual(zero_letters.parse(''), [])

        self.assertRaises(ParseError, zero_letters.parse, 'x')

    def test_times(self):
        three_letters = letter.times(3)
        self.assertEqual(three_letters.parse('xyz'), ['x', 'y', 'z'])

        self.assertRaises(ParseError, three_letters.parse, 'xy')
        self.assertRaises(ParseError, three_letters.parse, 'xyzw')

    def test_times_with_then(self):
        then_digit = letter.times(3) >> digit
        self.assertEqual(then_digit.parse('xyz1'), '1')

        self.assertRaises(ParseError, then_digit.parse, 'xy1')
        self.assertRaises(ParseError, then_digit.parse, 'xyz')
        self.assertRaises(ParseError, then_digit.parse, 'xyzw')

    def test_times_with_min_and_max(self):
        some_letters = letter.times(2, 4)

        self.assertEqual(some_letters.parse('xy'), ['x', 'y'])
        self.assertEqual(some_letters.parse('xyz'), ['x', 'y', 'z'])
        self.assertEqual(some_letters.parse('xyzw'), ['x', 'y', 'z', 'w'])

        self.assertRaises(ParseError, some_letters.parse, 'x')
        self.assertRaises(ParseError, some_letters.parse, 'xyzwv')

    def test_times_with_min_and_max_and_then(self):
        then_digit = letter.times(2, 4) >> digit

        self.assertEqual(then_digit.parse('xy1'), '1')
        self.assertEqual(then_digit.parse('xyz1'), '1')
        self.assertEqual(then_digit.parse('xyzw1'), '1')

        self.assertRaises(ParseError, then_digit.parse, 'xy')
        self.assertRaises(ParseError, then_digit.parse, 'xyzw')
        self.assertRaises(ParseError, then_digit.parse, 'xyzwv1')
        self.assertRaises(ParseError, then_digit.parse, 'x1')


if __name__ == '__main__':
    unittest.main()
