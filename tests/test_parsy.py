# -*- code: utf8 -*-
import enum
import re
import unittest
from collections import namedtuple
from datetime import date

from parsy import (
    ParseError,
    Stream,
    alt,
    any_char,
    char_from,
    decimal_digit,
    digit,
    forward_declaration,
    from_enum,
    generate,
    index,
    letter,
    line_info,
    line_info_at,
    match_item,
    peek,
    regex,
    seq,
    string,
    string_from,
)
from parsy import test_char as parsy_test_char  # to stop pytest thinking this function is a test
from parsy import test_item as parsy_test_item  # to stop pytest thinking this function is a test
from parsy import whitespace


class TestParser(unittest.TestCase):
    def test_string(self):
        parser = string("x")
        self.assertEqual(parser.parse(Stream("x")), "x")

        self.assertRaises(ParseError, parser.parse, Stream("y"))

    def test_string_transform(self):
        parser = string("x", transform=lambda s: s.lower())
        self.assertEqual(parser.parse(Stream("x")), "x")
        self.assertEqual(parser.parse(Stream("X")), "x")

        self.assertRaises(ParseError, parser.parse, Stream("y"))

    def test_string_transform_2(self):
        parser = string("Cat", transform=lambda s: s.lower())
        self.assertEqual(parser.parse(Stream("cat")), "Cat")
        self.assertEqual(parser.parse(Stream("CAT")), "Cat")
        self.assertEqual(parser.parse(Stream("CaT")), "Cat")

        self.assertRaises(ParseError, parser.parse, Stream("dog"))

    def test_regex_str(self):
        parser = regex(r"[0-9]")

        self.assertEqual(parser.parse(Stream("1")), "1")
        self.assertEqual(parser.parse(Stream("4")), "4")

        self.assertRaises(ParseError, parser.parse, Stream("x"))

    def test_regex_bytes(self):
        parser = regex(rb"[0-9]")

        self.assertEqual(parser.parse(Stream(b"1")), b"1")
        self.assertEqual(parser.parse(Stream(b"4")), b"4")

        self.assertRaises(ParseError, parser.parse, Stream(b"x"))

    def test_regex_compiled(self):
        parser = regex(re.compile(r"[0-9]"))
        self.assertEqual(parser.parse(Stream("1")), "1")
        self.assertRaises(ParseError, parser.parse, Stream("x"))

    def test_regex_group_number(self):
        parser = regex(re.compile(r"a([0-9])b"), group=1)
        self.assertEqual(parser.parse(Stream("a1b")), "1")
        self.assertRaises(ParseError, parser.parse, Stream("x"))

    def test_regex_group_name(self):
        parser = regex(re.compile(r"a(?P<name>[0-9])b"), group="name")
        self.assertEqual(parser.parse(Stream("a1b")), "1")
        self.assertRaises(ParseError, parser.parse, Stream("x"))

    def test_regex_group_tuple(self):
        parser = regex(re.compile(r"a([0-9])b([0-9])c"), group=(1, 2))
        self.assertEqual(parser.parse(Stream("a1b2c")), ("1", "2"))
        self.assertRaises(ParseError, parser.parse, Stream("x"))

    def test_then(self):
        xy_parser = string("x") >> string("y")
        self.assertEqual(xy_parser.parse(Stream("xy")), "y")

        self.assertRaises(ParseError, xy_parser.parse, Stream("y"))
        self.assertRaises(ParseError, xy_parser.parse, Stream("z"))

    def test_bind(self):
        piped = None

        def binder(x):
            nonlocal piped
            piped = x
            return string("y")

        parser = string("x").bind(binder)

        self.assertEqual(parser.parse(Stream("xy")), "y")
        self.assertEqual(piped, "x")

        self.assertRaises(ParseError, parser.parse, Stream("x"))

    def test_map(self):
        parser = digit.map(int)
        self.assertEqual(parser.parse(Stream("7")), 7)

    def test_combine(self):
        parser = seq(digit, letter).combine(lambda d, l: (d, l))
        self.assertEqual(parser.parse(Stream("1A")), ("1", "A"))

    def test_combine_dict(self):
        ddmmyyyy = (
            seq(
                regex(r"[0-9]{2}").map(int).tag("day"),
                regex(r"[0-9]{2}").map(int).tag("month"),
                regex(r"[0-9]{4}").map(int).tag("year"),
            )
            .map(dict)
            .combine_dict(date)
        )
        self.assertEqual(ddmmyyyy.parse(Stream("05042003")), date(2003, 4, 5))

    def test_combine_dict_list(self):
        Pair = namedtuple("Pair", ["word", "number"])
        parser = seq(
            regex(r"[A-Z]+").tag("word"),
            regex(r"[0-9]+").map(int).tag("number"),
        ).combine_dict(Pair)
        self.assertEqual(parser.parse(Stream("ABC123")), Pair(word="ABC", number=123))

    def test_combine_dict_skip_None(self):
        Pair = namedtuple("Pair", ["word", "number"])
        parser = seq(
            regex(r"[A-Z]+").tag("word"),
            whitespace.tag(None),
            regex(r"[0-9]+").map(int).tag("number"),
        ).combine_dict(Pair)
        self.assertEqual(parser.parse(Stream("ABC   123")), Pair(word="ABC", number=123))

    def test_combine_dict_skip_underscores(self):
        Pair = namedtuple("Pair", ["word", "number"])
        parser = seq(
            regex(r"[A-Z]+").tag("word"),
            whitespace.tag("_whitespace"),
            regex(r"[0-9]+").map(int).tag("number"),
        ).combine_dict(Pair)
        self.assertEqual(parser.parse(Stream("ABC   123")), Pair(word="ABC", number=123))

    def test_concat(self):
        parser = letter.many().concat()
        self.assertEqual(parser.parse(Stream("")), "")
        self.assertEqual(parser.parse(Stream("abc")), "abc")

    def test_concat_from_byte_stream(self):
        any_byte = parsy_test_item(lambda c: True, "any byte")
        parser = any_byte.map(lambda b: b.decode("ascii")).many().concat()
        self.assertEqual(parser.parse(Stream(b"")), "")
        self.assertEqual(parser.parse(Stream(b"abc")), "abc")

    def test_generate(self):
        x = y = None

        @generate
        def xy():
            nonlocal x
            nonlocal y
            x = yield string("x")
            y = yield string("y")
            return 3

        self.assertEqual(xy.parse(Stream("xy")), 3)
        self.assertEqual(x, "x")
        self.assertEqual(y, "y")

    def test_generate_return_parser(self):
        @generate
        def example():
            yield string("x")
            return string("y")

        self.assertEqual(example.parse(Stream("xy")), "y")

    def test_mark(self):
        parser = (letter.many().mark() << string("\n")).many()

        lines = parser.parse(Stream("asdf\nqwer\n"))

        self.assertEqual(len(lines), 2)

        (start, letters, end) = lines[0]
        self.assertEqual(start, (0, 0))
        self.assertEqual(letters, ["a", "s", "d", "f"])
        self.assertEqual(end, (0, 4))

        (start, letters, end) = lines[1]
        self.assertEqual(start, (1, 0))
        self.assertEqual(letters, ["q", "w", "e", "r"])
        self.assertEqual(end, (1, 4))

    def test_tag(self):
        parser = letter.many().concat().tag("word")
        self.assertEqual(
            parser.sep_by(string(",")).parse(Stream("this,is,a,list")),
            [("word", "this"), ("word", "is"), ("word", "a"), ("word", "list")],
        )

    def test_tag_map_dict(self):
        parser = seq(letter.tag("first_letter"), letter.many().concat().tag("remainder")).map(dict)
        self.assertEqual(parser.parse(Stream("Hello")), {"first_letter": "H", "remainder": "ello"})

    def test_generate_desc(self):
        @generate("a thing")
        def thing():
            yield string("t")

        with self.assertRaises(ParseError) as err:
            thing.parse(Stream("x"))

        ex = err.exception

        self.assertEqual(ex.expected, frozenset(["a thing"]))
        self.assertEqual(ex.stream, Stream("x"))
        self.assertEqual(ex.index, 0)

    def test_generate_default_desc(self):
        # We shouldn't give a default desc, the messages from the internal
        # parsers should bubble up.
        @generate
        def thing():
            yield string("a")
            yield string("b")

        with self.assertRaises(ParseError) as err:
            thing.parse(Stream("ax"))

        ex = err.exception

        self.assertEqual(ex.expected, frozenset(["b"]))
        self.assertEqual(ex.stream, Stream("ax"))
        self.assertEqual(ex.index, 1)

        self.assertIn("expected 'b' at 0:1", str(ex))

    def test_multiple_failures(self):
        abc = string("a") | string("b") | string("c")

        with self.assertRaises(ParseError) as err:
            abc.parse(Stream("d"))

        ex = err.exception
        self.assertEqual(ex.expected, frozenset(["a", "b", "c"]))
        self.assertEqual(str(ex), "expected one of 'a', 'b', 'c' at 0:0")

    def test_generate_backtracking(self):
        @generate
        def xy():
            yield string("x")
            yield string("y")
            assert False

        parser = xy | string("z")
        # should not finish executing xy()
        self.assertEqual(parser.parse(Stream("z")), "z")

    def test_or(self):
        x_or_y = string("x") | string("y")

        self.assertEqual(x_or_y.parse(Stream("x")), "x")
        self.assertEqual(x_or_y.parse(Stream("y")), "y")

    def test_or_with_then(self):
        parser = (string("\\") >> string("y")) | string("z")
        self.assertEqual(parser.parse(Stream("\\y")), "y")
        self.assertEqual(parser.parse(Stream("z")), "z")

        self.assertRaises(ParseError, parser.parse, Stream("\\z"))

    def test_many(self):
        letters = letter.many()
        self.assertEqual(letters.parse(Stream("x")), ["x"])
        self.assertEqual(letters.parse(Stream("xyz")), ["x", "y", "z"])
        self.assertEqual(letters.parse(Stream("")), [])

        self.assertRaises(ParseError, letters.parse, Stream("1"))

    def test_many_with_then(self):
        parser = string("x").many() >> string("y")
        self.assertEqual(parser.parse(Stream("y")), "y")
        self.assertEqual(parser.parse(Stream("xy")), "y")
        self.assertEqual(parser.parse(Stream("xxxxxy")), "y")

    def test_times_zero(self):
        zero_letters = letter.times(0)
        self.assertEqual(zero_letters.parse(Stream("")), [])

        self.assertRaises(ParseError, zero_letters.parse, Stream("x"))

    def test_times(self):
        three_letters = letter.times(3)
        self.assertEqual(three_letters.parse(Stream("xyz")), ["x", "y", "z"])

        self.assertRaises(ParseError, three_letters.parse, Stream("xy"))
        self.assertRaises(ParseError, three_letters.parse, Stream("xyzw"))

    def test_times_with_then(self):
        then_digit = letter.times(3) >> digit
        self.assertEqual(then_digit.parse(Stream("xyz1")), "1")

        self.assertRaises(ParseError, then_digit.parse, Stream("xy1"))
        self.assertRaises(ParseError, then_digit.parse, Stream("xyz"))
        self.assertRaises(ParseError, then_digit.parse, Stream("xyzw"))

    def test_times_with_min_and_max(self):
        some_letters = letter.times(2, 4)

        self.assertEqual(some_letters.parse(Stream("xy")), ["x", "y"])
        self.assertEqual(some_letters.parse(Stream("xyz")), ["x", "y", "z"])
        self.assertEqual(some_letters.parse(Stream("xyzw")), ["x", "y", "z", "w"])

        self.assertRaises(ParseError, some_letters.parse, Stream("x"))
        self.assertRaises(ParseError, some_letters.parse, Stream("xyzwv"))

    def test_times_with_min_and_max_and_then(self):
        then_digit = letter.times(2, 4) >> digit

        self.assertEqual(then_digit.parse(Stream("xy1")), "1")
        self.assertEqual(then_digit.parse(Stream("xyz1")), "1")
        self.assertEqual(then_digit.parse(Stream("xyzw1")), "1")

        self.assertRaises(ParseError, then_digit.parse, Stream("xy"))
        self.assertRaises(ParseError, then_digit.parse, Stream("xyzw"))
        self.assertRaises(ParseError, then_digit.parse, Stream("xyzwv1"))
        self.assertRaises(ParseError, then_digit.parse, Stream("x1"))

    def test_at_most(self):
        ab = string("ab")
        self.assertEqual(ab.at_most(2).parse(Stream("")), [])
        self.assertEqual(ab.at_most(2).parse(Stream("ab")), ["ab"])
        self.assertEqual(ab.at_most(2).parse(Stream("abab")), ["ab", "ab"])
        self.assertRaises(ParseError, ab.at_most(2).parse, Stream("ababab"))

    def test_until(self):

        until = string("s").until(string("x"))

        s = "ssssx"
        self.assertEqual(until.parse_partial(s), (4 * ["s"], "x"))
        self.assertEqual(seq(until, string("x")).parse(s), [4 * ["s"], "x"])
        self.assertEqual(until.then(string("x")).parse(s), "x")

        s = "ssssxy"
        self.assertEqual(until.parse_partial(s), (4 * ["s"], "xy"))
        self.assertEqual(seq(until, string("x")).parse_partial(s), ([4 * ["s"], "x"], "y"))
        self.assertEqual(until.then(string("x")).parse_partial(s), ("x", "y"))

        self.assertRaises(ParseError, until.parse, Stream("ssssy"))
        self.assertRaises(ParseError, until.parse, Stream("xssssxy"))

        self.assertEqual(until.parse_partial("xxx"), ([], "xxx"))

        until = regex(".").until(string("x"))
        self.assertEqual(until.parse_partial("xxxx"), ([], "xxxx"))

    def test_until_with_consume_other(self):

        until = string("s").until(string("x"), consume_other=True)

        self.assertEqual(until.parse(Stream("ssssx")), 4 * ["s"] + ["x"])
        self.assertEqual(until.parse_partial("ssssxy"), (4 * ["s"] + ["x"], "y"))

        self.assertEqual(until.parse_partial("xxx"), (["x"], "xx"))

        self.assertRaises(ParseError, until.parse, Stream("ssssy"))
        self.assertRaises(ParseError, until.parse, Stream("xssssxy"))

    def test_until_with_min(self):

        until = string("s").until(string("x"), min=3)

        self.assertEqual(until.parse_partial("sssx"), (3 * ["s"], "x"))
        self.assertEqual(until.parse_partial("sssssx"), (5 * ["s"], "x"))

        self.assertRaises(ParseError, until.parse_partial, "ssx")

    def test_until_with_max(self):

        # until with max
        until = string("s").until(string("x"), max=3)

        self.assertEqual(until.parse_partial("ssx"), (2 * ["s"], "x"))
        self.assertEqual(until.parse_partial("sssx"), (3 * ["s"], "x"))

        self.assertRaises(ParseError, until.parse_partial, "ssssx")

    def test_until_with_min_max(self):

        until = string("s").until(string("x"), min=3, max=5)

        self.assertEqual(until.parse_partial("sssx"), (3 * ["s"], "x"))
        self.assertEqual(until.parse_partial("sssssx"), (5 * ["s"], "x"))

        with self.assertRaises(ParseError) as cm:
            until.parse_partial("ssx")
        assert cm.exception.args[0] == frozenset({"at least 3 items; got 2 item(s)"})
        with self.assertRaises(ParseError) as cm:
            until.parse_partial("ssssssx")
        assert cm.exception.args[0] == frozenset({"at most 5 items"})

    def test_optional(self):
        p = string("a").optional()
        self.assertEqual(p.parse(Stream("a")), "a")
        self.assertEqual(p.parse(Stream("")), None)
        p = string("a").optional("b")
        self.assertEqual(p.parse(Stream("a")), "a")
        self.assertEqual(p.parse(Stream("")), "b")

    def test_sep_by(self):
        digit_list = digit.map(int).sep_by(string(","))

        self.assertEqual(digit_list.parse(Stream("1,2,3,4")), [1, 2, 3, 4])
        self.assertEqual(digit_list.parse(Stream("9,0,4,7")), [9, 0, 4, 7])
        self.assertEqual(digit_list.parse(Stream("3,7")), [3, 7])
        self.assertEqual(digit_list.parse(Stream("8")), [8])
        self.assertEqual(digit_list.parse(Stream("")), [])

        self.assertRaises(ParseError, digit_list.parse, Stream("8,"))
        self.assertRaises(ParseError, digit_list.parse, Stream(",9"))
        self.assertRaises(ParseError, digit_list.parse, Stream("82"))
        self.assertRaises(ParseError, digit_list.parse, Stream("7.6"))

    def test_sep_by_with_min_and_max(self):
        digit_list = digit.map(int).sep_by(string(","), min=2, max=4)

        self.assertEqual(digit_list.parse(Stream("1,2,3,4")), [1, 2, 3, 4])
        self.assertEqual(digit_list.parse(Stream("9,0,4,7")), [9, 0, 4, 7])
        self.assertEqual(digit_list.parse(Stream("3,7")), [3, 7])

        self.assertRaises(ParseError, digit_list.parse, Stream("8"))
        self.assertRaises(ParseError, digit_list.parse, Stream(""))
        self.assertRaises(ParseError, digit_list.parse, Stream("8,"))
        self.assertRaises(ParseError, digit_list.parse, Stream(",9"))
        self.assertRaises(ParseError, digit_list.parse, Stream("82"))
        self.assertRaises(ParseError, digit_list.parse, Stream("7.6"))
        self.assertEqual(digit.sep_by(string(","), max=0).parse(Stream("")), [])

    def test_add(self):
        self.assertEqual((letter + digit).parse(Stream("a1")), "a1")

    def test_multiply(self):
        self.assertEqual((letter * 3).parse(Stream("abc")), ["a", "b", "c"])

    def test_multiply_range(self):
        self.assertEqual((letter * range(1, 2)).parse(Stream("a")), ["a"])
        self.assertRaises(ParseError, (letter * range(1, 2)).parse, Stream("aa"))

    # Primitives
    def test_alt(self):
        self.assertRaises(ParseError, alt().parse, Stream(""))
        self.assertEqual(alt(letter, digit).parse(Stream("a")), "a")
        self.assertEqual(alt(letter, digit).parse(Stream("1")), "1")
        self.assertRaises(ParseError, alt(letter, digit).parse, Stream("."))

    def test_seq(self):
        self.assertEqual(seq().parse(Stream("")), [])
        self.assertEqual(seq(letter).parse(Stream("a")), ["a"])
        self.assertEqual(seq(letter, digit).parse(Stream("a1")), ["a", "1"])
        self.assertRaises(ParseError, seq(letter, digit).parse, Stream("1a"))

    def test_seq_kwargs(self):
        self.assertEqual(
            seq(first_name=regex(r"\S+") << whitespace, last_name=regex(r"\S+")).parse(Stream("Jane Smith")),
            {"first_name": "Jane", "last_name": "Smith"},
        )

    def test_seq_kwargs_fail(self):
        self.assertRaises(ParseError, seq(a=string("a")).parse, Stream("b"))

    def test_seq_kwargs_error(self):
        self.assertRaises(ValueError, lambda: seq(string("a"), b=string("b")))

    def test_test_char(self):
        ascii = parsy_test_char(lambda c: ord(c) < 128, "ascii character")
        self.assertEqual(ascii.parse(Stream("a")), "a")
        with self.assertRaises(ParseError) as err:
            ascii.parse(Stream("☺"))
        ex = err.exception
        self.assertEqual(str(ex), """expected 'ascii character' at 0:0""")

        with self.assertRaises(ParseError) as err:
            ascii.parse(Stream(""))
        ex = err.exception
        self.assertEqual(str(ex), """expected 'ascii character' at 0:0""")

    def test_char_from_str(self):
        ab = char_from("ab")
        self.assertEqual(ab.parse(Stream("a")), "a")
        self.assertEqual(ab.parse(Stream("b")), "b")

        with self.assertRaises(ParseError) as err:
            ab.parse(Stream("x"))

        ex = err.exception
        self.assertEqual(str(ex), """expected '[ab]' at 0:0""")

    def test_char_from_bytes(self):
        ab = char_from(b"ab")
        self.assertEqual(ab.parse(Stream(b"a")), b"a")
        self.assertEqual(ab.parse(Stream(b"b")), b"b")

        with self.assertRaises(ParseError) as err:
            ab.parse(Stream(b"x"))

        ex = err.exception
        self.assertEqual(str(ex), """expected b'[ab]' at 0""")

    def test_string_from(self):
        titles = string_from("Mr", "Mr.", "Mrs", "Mrs.")
        self.assertEqual(titles.parse(Stream("Mr")), "Mr")
        self.assertEqual(titles.parse(Stream("Mr.")), "Mr.")
        self.assertEqual((titles + string(" Hyde")).parse(Stream("Mr. Hyde")), "Mr. Hyde")
        with self.assertRaises(ParseError) as err:
            titles.parse(Stream("foo"))

        ex = err.exception
        self.assertEqual(str(ex), """expected one of 'Mr', 'Mr.', 'Mrs', 'Mrs.' at 0:0""")

    def test_string_from_transform(self):
        titles = string_from("Mr", "Mr.", "Mrs", "Mrs.", transform=lambda s: s.lower())
        self.assertEqual(titles.parse(Stream("mr")), "Mr")
        self.assertEqual(titles.parse(Stream("mr.")), "Mr.")
        self.assertEqual(titles.parse(Stream("MR")), "Mr")
        self.assertEqual(titles.parse(Stream("MR.")), "Mr.")

    def test_peek(self):
        self.assertEqual(peek(any_char).parse_partial(Stream("abc")), ("a", "abc"))
        with self.assertRaises(ParseError) as err:
            peek(digit).parse(Stream("a"))
        self.assertEqual(str(err.exception), "expected 'a digit' at 0:0")

    def test_any_char(self):
        self.assertEqual(any_char.parse(Stream("x")), "x")
        self.assertEqual(any_char.parse(Stream("\n")), "\n")
        self.assertRaises(ParseError, any_char.parse, Stream(""))

    def test_whitespace(self):
        self.assertEqual(whitespace.parse(Stream("\n")), "\n")
        self.assertEqual(whitespace.parse(Stream(" ")), " ")
        self.assertRaises(ParseError, whitespace.parse, Stream("x"))

    def test_letter(self):
        self.assertEqual(letter.parse(Stream("a")), "a")
        self.assertRaises(ParseError, letter.parse, Stream("1"))

    def test_digit(self):
        self.assertEqual(digit.parse(Stream("¹")), "¹")
        self.assertEqual(digit.parse(Stream("2")), "2")
        self.assertRaises(ParseError, digit.parse, Stream("x"))

    def test_decimal_digit(self):
        self.assertEqual(decimal_digit.at_least(1).concat().parse(Stream("9876543210")), "9876543210")
        self.assertRaises(ParseError, decimal_digit.parse, Stream("¹"))

    def test_line_info(self):
        @generate
        def foo():
            i = yield line_info
            l = yield any_char
            return (l, i)

        self.assertEqual(
            foo.many().parse(Stream("AB\nCD")),
            [
                ("A", (None, 0, 0)),
                ("B", (None, 0, 1)),
                ("\n", (None, 0, 2)),
                ("C", (None, 1, 0)),
                ("D", (None, 1, 1)),
            ],
        )

    def test_should_fail(self):
        not_a_digit = digit.should_fail("not a digit") >> regex(r".*")

        self.assertEqual(not_a_digit.parse(Stream("a")), "a")
        self.assertEqual(not_a_digit.parse(Stream("abc")), "abc")
        self.assertEqual(not_a_digit.parse(Stream("a10")), "a10")
        self.assertEqual(not_a_digit.parse(Stream("")), "")

        with self.assertRaises(ParseError) as err:
            not_a_digit.parse(Stream("8"))
        self.assertEqual(str(err.exception), "expected 'not a digit' at 0:0")

        self.assertRaises(ParseError, not_a_digit.parse, Stream("8ab"))

    def test_from_enum_string(self):
        class Pet(enum.Enum):
            CAT = "cat"
            DOG = "dog"

        pet = from_enum(Pet)
        self.assertEqual(pet.parse(Stream("cat")), Pet.CAT)
        self.assertEqual(pet.parse(Stream("dog")), Pet.DOG)
        self.assertRaises(ParseError, pet.parse, Stream("foo"))

    def test_from_enum_int(self):
        class Position(enum.Enum):
            FIRST = 1
            SECOND = 2

        position = from_enum(Position)
        self.assertEqual(position.parse(Stream("1")), Position.FIRST)
        self.assertEqual(position.parse(Stream("2")), Position.SECOND)
        self.assertRaises(ParseError, position.parse, Stream("foo"))

    def test_from_enum_transform(self):
        class Pet(enum.Enum):
            CAT = "cat"
            DOG = "dog"

        pet = from_enum(Pet, transform=lambda s: s.lower())
        self.assertEqual(pet.parse(Stream("cat")), Pet.CAT)
        self.assertEqual(pet.parse(Stream("CAT")), Pet.CAT)


class TestParserTokens(unittest.TestCase):
    """
    Tests that ensure that `.parse` can handle an arbitrary list of tokens,
    rather than a string.
    """

    # Some opaque objects we will use in our stream:
    START = object()
    STOP = object()

    def test_test_item(self):
        start_stop = parsy_test_item(lambda i: i in [self.START, self.STOP], "START/STOP")
        self.assertEqual(start_stop.parse(Stream([self.START])), self.START)
        self.assertEqual(start_stop.parse(Stream([self.STOP])), self.STOP)
        with self.assertRaises(ParseError) as err:
            start_stop.many().parse(Stream([self.START, "hello"]))

        ex = err.exception
        self.assertEqual(str(ex), "expected one of 'EOF', 'START/STOP' at 1")
        self.assertEqual(ex.expected, {"EOF", "START/STOP"})
        self.assertEqual(ex.index, 1)

    def test_match_item(self):
        self.assertEqual(match_item(self.START).parse(Stream([self.START])), self.START)
        with self.assertRaises(ParseError) as err:
            match_item(self.START, "START").parse([])

        ex = err.exception
        self.assertEqual(str(ex), "expected 'START' at 0")

    def test_parse_tokens(self):
        other_vals = parsy_test_item(lambda i: i not in [self.START, self.STOP], "not START/STOP")

        bracketed = match_item(self.START) >> other_vals.many() << match_item(self.STOP)
        stream = Stream([self.START, "hello", 1, 2, "goodbye", self.STOP])
        result = bracketed.parse(stream)
        self.assertEqual(result, ["hello", 1, 2, "goodbye"])

    def test_index(self):
        @generate
        def foo():
            i = yield index
            l = yield letter
            return (l, i)

        self.assertEqual(foo.many().parse(Stream(["A", "B"])), [("A", 0), ("B", 1)])


class TestUtils(unittest.TestCase):
    def test_line_info_at(self):
        text = Stream("abc\ndef")
        self.assertEqual(line_info_at(text, 0), (None, 0, 0))
        self.assertEqual(line_info_at(text, 2), (None, 0, 2))
        self.assertEqual(line_info_at(text, 3), (None, 0, 3))
        self.assertEqual(line_info_at(text, 4), (None, 1, 0))
        self.assertEqual(line_info_at(text, 7), (None, 1, 3))
        self.assertRaises(ValueError, lambda: line_info_at(text, 8))


class TestForwardDeclaration(unittest.TestCase):
    def test_forward_declaration_1(self):
        # This is the example from the docs
        expr = forward_declaration()
        with self.assertRaises(ValueError):
            expr.parse(Stream("()"))

        with self.assertRaises(ValueError):
            expr.parse_partial("()")

        simple = regex("[0-9]+").map(int)
        group = string("(") >> expr.sep_by(string(" ")) << string(")")
        expr.become(simple | group)

        self.assertEqual(expr.parse(Stream("(0 1 (2 3))")), [0, 1, [2, 3]])

    def test_forward_declaration_2(self):
        # Simplest example I could think of
        expr = forward_declaration()
        expr.become(string("A") + expr | string("Z"))

        self.assertEqual(expr.parse(Stream("Z")), "Z")
        self.assertEqual(expr.parse(Stream("AZ")), "AZ")
        self.assertEqual(expr.parse(Stream("AAAAAZ")), "AAAAAZ")

        with self.assertRaises(ParseError):
            expr.parse(Stream("A"))

        with self.assertRaises(ParseError):
            expr.parse(Stream("B"))

        self.assertEqual(expr.parse_partial("AAZXX"), ("AAZ", "XX"))

    def test_forward_declaration_cant_become_twice(self):
        dec = forward_declaration()
        other = string("X")
        dec.become(other)

        with self.assertRaises((AttributeError, TypeError)):
            dec.become(other)


if __name__ == "__main__":
    unittest.main()
