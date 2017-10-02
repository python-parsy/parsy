# -*- code: utf8 -*-
import unittest

from parsy import test as parsy_test  # to stop pytest thinking this function is a test
from parsy import ParseError, digit, generate, letter, line_info_at, one_of, regex, seq, string


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

    def test_generate_default_desc(self):
        # We shouldn't give a default desc, the messages from the internal
        # parsers should bubble up.
        @generate
        def thing():
            yield string('a')
            yield string('b')

        with self.assertRaises(ParseError) as err:
            thing.parse('ax')

        ex = err.exception

        self.assertEqual(ex.expected, frozenset(['b']))
        self.assertEqual(ex.stream, 'ax')
        self.assertEqual(ex.index, 1)

        self.assertIn("expected 'b' at 0:1",
                      str(ex))

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

    def test_sep_by(self):
        digit_list = digit.map(int).sep_by(string(','))

        self.assertEqual(digit_list.parse('1,2,3,4'), [1, 2, 3, 4])
        self.assertEqual(digit_list.parse('9,0,4,7'), [9, 0, 4, 7])
        self.assertEqual(digit_list.parse('3,7'), [3, 7])
        self.assertEqual(digit_list.parse('8'), [8])
        self.assertEqual(digit_list.parse(''), [])

        self.assertRaises(ParseError, digit_list.parse, '8,')
        self.assertRaises(ParseError, digit_list.parse, ',9')
        self.assertRaises(ParseError, digit_list.parse, '82')
        self.assertRaises(ParseError, digit_list.parse, '7.6')

    def test_sep_by_with_min_and_max(self):
        digit_list = digit.map(int).sep_by(string(','), min=2, max=4)

        self.assertEqual(digit_list.parse('1,2,3,4'), [1, 2, 3, 4])
        self.assertEqual(digit_list.parse('9,0,4,7'), [9, 0, 4, 7])
        self.assertEqual(digit_list.parse('3,7'), [3, 7])

        self.assertRaises(ParseError, digit_list.parse, '8')
        self.assertRaises(ParseError, digit_list.parse, '')
        self.assertRaises(ParseError, digit_list.parse, '8,')
        self.assertRaises(ParseError, digit_list.parse, ',9')
        self.assertRaises(ParseError, digit_list.parse, '82')
        self.assertRaises(ParseError, digit_list.parse, '7.6')

    def test_test(self):
        ascii = parsy_test(lambda c: ord(c) < 128,
                           "ascii character")
        self.assertEqual(ascii.parse("a"), "a")
        with self.assertRaises(ParseError) as err:
            ascii.parse('☺')
        ex = err.exception
        self.assertEqual(str(ex), """expected 'ascii character' at 0:0""")

    def test_one_of_string(self):
        ab = one_of("ab")
        self.assertEqual(ab.parse("a"), "a")
        self.assertEqual(ab.parse("b"), "b")

        with self.assertRaises(ParseError) as err:
            ab.parse('x')

        ex = err.exception
        self.assertEqual(str(ex), """expected "one of 'ab'" at 0:0""")

    def test_one_of_string_list(self):
        titles = one_of(["Mr", "Mr.", "Mrs", "Mrs."])
        self.assertEqual(titles.parse("Mr"), "Mr")
        self.assertEqual(titles.parse("Mr."), "Mr.")
        self.assertEqual((titles + string(" Hyde")).parse("Mr. Hyde"),
                         "Mr. Hyde")
        with self.assertRaises(ParseError) as err:
            titles.parse('foo')

        ex = err.exception
        self.assertEqual(str(ex), """expected one of 'Mr', 'Mr.', 'Mrs', 'Mrs.' at 0:0""")


class TestUtils(unittest.TestCase):
    def test_line_info_at(self):
        text = "abc\ndef"
        self.assertEqual(line_info_at(text, 0),
                         (0, 0))
        self.assertEqual(line_info_at(text, 2),
                         (0, 2))
        self.assertEqual(line_info_at(text, 3),
                         (0, 3))
        self.assertEqual(line_info_at(text, 4),
                         (1, 0))
        self.assertEqual(line_info_at(text, 7),
                         (1, 3))
        self.assertRaises(ValueError, lambda: line_info_at(text, 8))


if __name__ == '__main__':
    unittest.main()
