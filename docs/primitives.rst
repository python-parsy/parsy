==================
Parsing primitives
==================

These are the lowest level building blocks for creating parsers.

.. module:: parsy

.. function:: string(expected_string)

   Returns a parser that expects the ``expected_string`` and produces
   that string value.

.. function:: regex(exp, flags=0)

   Returns a parser that expects the given ``exp``, and produces the
   matched string. ``exp`` can be a compiled regular expression, or a
   string which will be compiled with the given ``flags``.

.. function:: test_char(func, description)

   Returns a parser that tests a single character with the callable
   ``func``. If ``func`` returns ``True``, the parse succeeds, otherwise
   the parse fails with the description ``description``.

   .. code-block:: python

      >>> ascii = test_char(lambda c: ord(c) < 128,
                            "ascii character")
      >>> ascii.parse("A")
      'A'

.. function:: char_from(characters)

   Accepts a string and returns a parser that matches and returns one character
   from the string.

   .. code-block:: python

      >>> char_from("abc").parse("a")
      'a'

.. function:: string_from(*strings)

   Accepts a sequence of strings as positional arguments, and returns a parser
   that matches and returns one string from the list. The list is first sorted
   in descending length order, so that overlapping strings are handled correctly
   by checking the longest one first.

   .. code-block:: python

      >>> string_from("y", "yes").parse("yes")
      'yes'

.. function:: success(val)

   Returns a parser that does not consume any of the stream, but
   produces ``val``.

.. function:: fail(expected)

   Returns a parser that always fails with the provided error message.

.. data:: any_char

   A parser that matches any single character.

.. data:: whitespace

   A parser that matches and returns one or more whitespace characters

.. data:: letter

   A parser that matches and returns a single letter, as defined by
   ``str.isalpha``.

.. data:: digit

   A parser that matches and returns a single digit, as defined by
   ``str.isdigit``. Note that this includes various unicode characters
   outside of the normal 0-9 range, such as ¹²³.

.. data:: decimal_digit

   A parser that matches and returns a single decimal digit, one of
   "0123456789".
