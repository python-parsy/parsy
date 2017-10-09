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

   Using a regex parser for small building blocks, instead of building up
   parsers from primitives like :func:`string`, :func:`test_char` and
   :meth:`Parser.times` combinators etc., can have several advantages,
   including:

   * It can be more succinct e.g. compare:

     .. code-block:: python

        >>> (string('a') | string('b')).times(1, 4)
        >>> regex(r'[ab]{1,4}')

   * It will return the entire matched string as a single item,
     so you don't need to use :meth:`Parser.concat`.
   * It can be much faster.

.. function:: test_char(func, description)

   Returns a parser that tests a single character with the callable
   ``func``. If ``func`` returns ``True``, the parse succeeds, otherwise
   the parse fails with the description ``description``.

   .. code-block:: python

      >>> ascii = test_char(lambda c: ord(c) < 128,
      ...                   'ascii character')
      >>> ascii.parse('A')
      'A'

.. function:: test_item(func, description)

   Returns a parser that tests a single item from the list of items being
   consumed, using the callable ``func``. If ``func`` returns ``True``, the
   parse succeeds, otherwise the parse fails with the description
   ``description``.

   If you are parsing a string, i.e. a list of characters, you can use
   :func:`test_char` instead. (In fact the implementations are identical, these
   functions are aliases for the sake of clear code).

   .. code-block:: python

      >>> numeric = test_item(str.isnumeric, 'numeric')
      >>> numeric.many().parse(['123', '456'])
      ['123', '456']

.. function:: char_from(characters)

   Accepts a string and returns a parser that matches and returns one character
   from the string.

   .. code-block:: python

      >>> char_from('abc').parse('a')
      'a'

.. function:: string_from(*strings)

   Accepts a sequence of strings as positional arguments, and returns a parser
   that matches and returns one string from the list. The list is first sorted
   in descending length order, so that overlapping strings are handled correctly
   by checking the longest one first.

   .. code-block:: python

      >>> string_from('y', 'yes').parse('yes')
      'yes'


.. function:: match_item(item, description=None)

   Returns a parser that tests the next item (or character) from the stream (or
   string) for equality against the provided item. Optionally a string
   description can be passed.

   Parsing a string:

   >>> letter_A = match_item('A')
   >>> letter_A.parse_partial('ABC')
   ('A', 'BC')

   Parsing a list of tokens:

   >>> hello = match_item('hello')
   >>> hello.parse_partial(['hello', 'how', 'are', 'you'])
   ('hello', ['how', 'are', 'you'])

.. function:: success(val)

   Returns a parser that does not consume any of the stream, but
   produces ``val``.

.. function:: fail(expected)

   Returns a parser that always fails with the provided error message.

Pre-built parsers
=================

Some common, pre-built parsers (all of these are :class:`Parser` objects created
using the primitives above):


.. data:: any_char

   A parser that matches any single character.

.. data:: whitespace

   A parser that matches and returns one or more whitespace characters.

.. data:: letter

   A parser that matches and returns a single letter, as defined by
   `str.isalpha <https://docs.python.org/3/library/stdtypes.html#str.isalpha>`_.

.. data:: digit

   A parser that matches and returns a single digit, as defined by `str.isdigit
   <https://docs.python.org/3/library/stdtypes.html#str.isdigit>`_. Note that
   this includes various unicode characters outside of the normal 0-9 range,
   such as ¹²³.

.. data:: decimal_digit

   A parser that matches and returns a single decimal digit, one of
   "0123456789".

.. data:: line_info

   A parser that consumes no input and always just returns the current line
   information, a tuple of (line, column), zero-indexed, where lines are
   terminated by ``\n``. This is normally useful when wanting to build more
   debugging information into parse failure error messages.

.. data:: index

   A parser that consumes no input and always just returns the current stream
   index. This is normally useful when wanting to build more debugging
   information into parse failure error messages.
