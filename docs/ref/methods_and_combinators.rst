=========================================
Parser methods, operators and combinators
=========================================

Parser methods
==============

Parser objects are returned by any of the built-in parser :doc:`primitives`. They
can be used and manipulated as below.

.. currentmodule:: parsy

.. class:: Parser

   .. method:: __init__(wrapped_fn)

      This is a low level function to create new parsers that is used internally
      but is rarely needed by users of the parsy library. It should be passed a
      parsing function, which takes two arguments - a string/list to be parsed
      and the current index into the list - and returns a :class:`Result` object,
      as described in :doc:`/ref/parser_instances`.

   The following methods are for actually **using** the parsers that you have
   created:

   .. method:: parse(string_or_list)

      Attempts to parse the given string (or list). If the parse is successful
      and consumes the entire string, the result is returned - otherwise, a
      ``ParseError`` is raised.

      Instead of passing a string, you can in fact pass a list of tokens. Almost
      all the examples assume strings for simplicity. Some of the primitives are
      also clearly string specific, and a few of the combinators (such as
      :meth:`Parser.concat`) are string specific, but most of the rest of the
      library will work with tokens just as well. See :doc:`/howto/lexing` for
      more information.

   .. method:: parse_partial(string_or_list)

      Similar to ``parse``, except that it does not require the entire
      string (or list) to be consumed. Returns a tuple of
      ``(result, remainder)``, where ``remainder`` is the part of
      the string (or list) that was left over.

   The following methods are essentially **combinators** that produce new
   parsers from the existing one. They are provided as methods on ``Parser`` for
   convenience. More combinators are documented below.

   .. method:: desc(string)

      Adds a description to the parser, which is used in the error message
      if parsing fails.

      >>> year = regex(r'[0-9]{4}').desc('4 digit year')
      >>> year.parse('123')
      ParseError: expected 4 digit year at 0:0

   .. method:: then(other_parser)

      Returns a parser which, if the initial parser succeeds, will continue parsing
      with ``other_parser``. This will produce the value produced by
      ``other_parser``.

      .. code:: python

         >>> string('x').then(string('y')).parse('xy')
         'y'

      See also :ref:`parser-rshift`.

   .. method:: skip(other_parser)

      Similar to :meth:`Parser.then`, except the resulting parser will use
      the value produced by the first parser.

      .. code:: python

         >>> string('x').skip(string('y')).parse('xy')
         'x'

      See also :ref:`parser-lshift`.

   .. method:: many()

      Returns a parser that expects the initial parser 0 or more times, and
      produces a list of the results. Note that this parser does not fail if
      nothing matches, but instead consumes nothing and produces an empty list.

      .. code:: python

         >>> parser = regex(r'[a-z]').many()
         >>> parser.parse('')
         []
         >>> parser.parse('abc')
         ['a', 'b', 'c']

   .. method:: times(min [, max=min])

      Returns a parser that expects the initial parser at least ``min`` times,
      and at most ``max`` times, and produces a list of the results. If only one
      argument is given, the parser is expected exactly that number of times.

   .. method:: at_most(n)

      Returns a parser that expects the initial parser at most ``n`` times, and
      produces a list of the results.

   .. method:: at_least(n)

      Returns a parser that expects the initial parser at least ``n`` times, and
      produces a list of the results.

   .. method:: optional()

      Returns a parser that expects the initial parser zero or once, and maps
      the result to ``None`` in the case of no match.

      .. code:: python

         >>> string('A').optional().parse('A')
         'A'
         >>> string('A').optional().parse('')
         None

   .. method:: map(fn)

      Returns a parser that transforms the produced value of the initial parser
      with ``fn``.

      .. code:: python

         >>> regex(r'[0-9]+').map(int).parse('1234')
         1234

      This is the simplest way to convert parsed strings into the data types
      that you need. See also :meth:`combine` and :meth:`combine_dict` below.

   .. method:: combine(fn)

      Returns a parser that transforms the produced values of the initial parser
      with ``fn``, passing the arguments using ``*args`` syntax.

      Where the current parser produces an iterable of values, this can be a
      more convenient way to combine them than :meth:`~Parser.map`.

      Example 1 - the argument order of our callable already matches:

      .. code:: python

         >>> from datetime import date
         >>> yyyymmdd = seq(regex(r'[0-9]{4}').map(int),
         ...                regex(r'[0-9]{2}').map(int),
         ...                regex(r'[0-9]{2}').map(int)).combine(date)
         >>> yyyymmdd.parse('20140506')
         datetime.date(2014, 5, 6)

      Example 2 - the argument order of our callable doesn't match, and
      we need to adjust a parameter, so we can fix it using a lambda.

      .. code:: python

         >>> ddmmyy = regex(r'[0-9]{2}').map(int).times(3).combine(
         ...                lambda d, m, y: date(2000 + y, m, d))
         >>> ddmmyy.parse('060514')
         datetime.date(2014, 5, 6)

      The equivalent ``lambda`` to use with ``map`` would be ``lambda res:
      date(2000 + res[2], res[1], res[0])``, which is less readable. The version
      with ``combine`` also ensures that exactly 3 items are generated by the
      previous parser, otherwise you get a ``TypeError``.

   .. method:: combine_dict(fn)

      Returns a parser that transforms the value produced by the initial parser
      using the supplied function/callable, passing the arguments using the
      ``**kwargs`` syntax.

      The value produced by the initial parser must be a mapping/dictionary from
      names to values, or a list of two-tuples, or something else that can be
      passed to the ``dict`` constructor.

      If ``None`` is present as a key in the dictionary it will be removed
      before passing to ``fn``, as will all keys starting with ``_``.

      Motivation:

      For building complex objects, this can be more convenient, flexible and
      readable than :meth:`map` or :meth:`combine`, because by avoiding
      positional arguments we can avoid a dependence on the order of components
      in the string being parsed and in the argument order of callables being
      used. It is especially designed to be used in conjunction with :func:`seq`
      and :meth:`tag`.

      **For Python 3.6 and above,** we can make use of the ``**kwargs`` version
      of :func:`seq` to produce a very readable definition:

      .. code:: python

         >>> ddmmyyyy = seq(
         ...     day=regex(r'[0-9]{2}').map(int),
         ...     month=regex(r'[0-9]{2}').map(int),
         ...     year=regex(r'[0-9]{4}').map(int),
         ... ).combine_dict(date)
         >>> ddmmyyyy.parse('04052003')
         datetime.date(2003, 5, 4)

      (If that is hard to understand, use a Python REPL, and examine the result
      of the ``parse`` call if you remove the ``combine_dict`` call).

      Here we used ``datetime.date`` which accepts keyword arguments. For your
      own parsing needs you will often use custom data types. You can create
      these however you like, but we recommend `attrs
      <https://attrs.readthedocs.io/en/stable/>`_. You can also use `namedtuple
      <https://docs.python.org/3.6/library/collections.html#collections.namedtuple>`_
      from the standard library for simple cases, or `dataclasses
      <https://docs.python.org/3/library/dataclasses.html>`_.

      The following example shows the use of ``_`` as a prefix to remove
      elements you are not interested in, and the use of ``namedtuple`` to
      create a simple data-structure.

      .. code-block:: python

         >>> from collections import namedtuple
         >>> Pair = namedtuple('Pair', ['name', 'value'])
         >>> name = regex("[A-Za-z]+")
         >>> int_value = regex("[0-9]+").map(int)
         >>> bool_value = string("true").result(True) | string("false").result(False)
         >>> pair = seq(
         ...    name=name,
         ...    __eq=string('='),
         ...    value=int_value | bool_value,
         ...    __sc=string(';'),
         ... ).combine_dict(Pair)
         >>> pair.parse("foo=123;")
         Pair(name='foo', value=123)
         >>> pair.parse("BAR=true;")
         Pair(name='BAR', value=True)

      You could also use ``<<`` or ``>>`` for the unwanted parts (but in some
      cases this is less convenient):

      .. code-block:: python

         >>> pair = seq(
         ...    name=name << string('='),
         ...    value=(int_value | bool_value) << string(';')
         ... ).combine_dict(Pair)

      **For Python 3.5 and below**, kwargs usage is not possible (because
      keyword arguments produce a dictionary that does not have a guaranteed
      order). Instead, use :meth:`tag` to produce a list of name-value pairs:

      .. code:: python

         >>> ddmmyyyy = seq(
         ...     regex(r'[0-9]{2}').map(int).tag('day'),
         ...     regex(r'[0-9]{2}').map(int).tag('month'),
         ...     regex(r'[0-9]{4}').map(int).tag('year'),
         ... ).combine_dict(date)
         >>> ddmmyyyy.parse('04052003')
         datetime.date(2003, 5, 4)

      The following example shows the use of ``tag(None)`` to remove
      elements you are not interested in, and the use of ``namedtuple`` to
      create a simple data-structure.

      .. code-block:: python

         >>> from collections import namedtuple
         >>> Pair = namedtuple('Pair', ['name', 'value'])
         >>> name = regex("[A-Za-z]+")
         >>> int_value = regex("[0-9]+").map(int)
         >>> bool_value = string("true").result(True) | string("false").result(False)
         >>> pair = seq(
         ...    name.tag('name'),
         ...    string('=').tag(None),
         ...    (int_value | bool_value).tag('value'),
         ...    string(';').tag(None),
         ... ).combine_dict(Pair)
         >>> pair.parse("foo=123;")
         Pair(name='foo', value=123)
         >>> pair.parse("BAR=true;")
         Pair(name='BAR', value=True)

      You could also use ``<<`` for the unwanted parts instead of ``.tag(None)``:

      .. code-block:: python

         >>> pair = seq(
         ...    name.tag('name') << string('='),
         ...    (int_value | bool_value).tag('value') << string(';')
         ... ).combine_dict(Pair)

      .. versionchanged:: 1.2
         Allow lists as well as dicts to be consumed, and filter out ``None``.

      .. versionchanged:: 1.3
         Stripping of args starting with ``_``

   .. method:: tag(name)

      Returns a parser that wraps the produced value of the initial parser in a
      2 tuple containing ``(name, value)``. This provides a very simple way to
      label parsed components. e.g.:

      .. code:: python

         >>> day = regex(r'[0-9]+').map(int)
         >>> month = string_from("January", "February", "March", "April", "May",
         ...                     "June", "July", "August", "September", "October",
         ...                     "November", "December")
         >>> day.parse("10")
         10
         >>> day.tag("day").parse("10")
         ('day', 10)

         >>> seq(day.tag("day") << whitespace,
         ...     month.tag("month")
         ...     ).parse("10 September")
         [('day', 10), ('month', 'September')]

      It also works well when combined with ``.map(dict)`` to get a dictionary
      of values:

      .. code:: python

         >>> seq(day.tag("name") << whitespace,
         ...     month.tag("month")
         ...     ).map(dict).parse("10 September")
         {'day': 10, 'month': 'September'}

      ... and with :meth:`combine_dict` to build other objects.

   .. method:: concat()

      Returns a parser that concatenates together (as a string) the previously
      produced values. Usually used after :meth:`~Parser.many` and similar
      methods that produce multiple values.

      .. code:: python

         >>> letter.at_least(1).parse("hello")
         ['h', 'e', 'l', 'l', 'o']
         >>> letter.at_least(1).concat().parse("hello")
         'hello'

   .. method:: result(val)

      Returns a parser that, if the initial parser succeeds, always produces
      ``val``.

      .. code:: python

         >>> string('foo').result(42).parse('foo')
         42

   .. method:: should_fail(description)

      Returns a parser that fails when the initial parser succeeds, and succeeds
      when the initial parser fails (consuming no input). A description must
      be passed which is used in parse failure messages.

      This is essentially a negative lookahead:

      .. code:: python

         >>> p = letter << string(" ").should_fail("not space")
         >>> p.parse('A')
         'A'
         >>> p.parse('A ')
         ParseError: expected 'not space' at 0:1

      It is also useful for implementing things like parsing repeatedly until a
      marker:

      .. code:: python

         >>> (string(";").should_fail("not ;") >> letter).many().concat().parse_partial('ABC;')
         ('ABC', ';')

   .. method:: bind(fn)

      Returns a parser which, if the initial parser is successful, passes the
      result to ``fn``, and continues with the parser returned from ``fn``. This
      is the monadic binding operation. However, since we don't have Haskell's
      ``do`` notation in Python, using this is very awkward. Instead, you should
      look at :doc:`/ref/generating/` which provides a much nicer syntax for that
      cases where you would have needed ``do`` notation in Parsec.

   .. method:: sep_by(sep, min=0, max=inf)

      Like :meth:`Parser.times`, this returns a new parser that repeats
      the initial parser and collects the results in a list, but in this case separated
      by the parser ``sep`` (whose return value is discarded). By default it
      repeats with no limit, but minimum and maximum values can be supplied.

      .. code:: python

         >>> csv = letter.at_least(1).concat().sep_by(string(","))
         >>> csv.parse("abc,def")
         ['abc', 'def']

   .. method:: mark()

      Returns a parser that wraps the initial parser's result in a value
      containing column and line information of the match, as well as the
      original value. The new value is a 3-tuple:

      .. code:: python

         ((start_row, start_column),
          original_value,
          (end_row, end_column))

      This is useful for being able to report problems with parsing more
      accurately, especially if you are using parsy as a :doc:`lexer
      </howto/lexing/>` and want subsequent parsing of the token stream to be
      able to report original positions in error messages etc.

.. _operators:

Parser operators
================

This section describes operators that you can use on :class:`Parser` objects to
build new parsers.


.. _parser-or:

``|`` operator
--------------

``parser | other_parser``

Returns a parser that tries ``parser`` and, if it fails, backtracks
and tries ``other_parser``. These can be chained together.

The resulting parser will produce the value produced by the first
successful parser.

.. code:: python

   >>> parser = string('x') | string('y') | string('z')
   >>> parser.parse('x')
   'x'
   >>> parser.parse('y')
   'y'
   >>> parser.parse('z')
   'z'

Note that ``other_parser`` will only be tried if ``parser`` cannot consume any
input and fails. ``other_parser`` is not used in the case that **later** parser
components fail. This means that the order of the operands matters - for
example:

.. code:: python

   >>> ((string('A') | string('AB')) + string('C')).parse('ABC')
   ParseEror: expected 'C' at 0:1
   >>> ((string('AB') | string('A')) + string('C')).parse('ABC')
   'ABC'
   >>> ((string('AB') | string('A')) + string('C')).parse('AC')
   'AC'

.. _parser-lshift:

``<<`` operator
---------------

``parser << other_parser``

The same as ``parser.skip(other_parser)`` - see :meth:`Parser.skip`.

(Hint - the arrows point at the important parser!)

.. code:: python

   >>> (string('x') << string('y')).parse('xy')
   'x'

.. _parser-rshift:

``>>`` operator
---------------

``parser >> other_parser``

The same as ``parser.then(other_parser)`` - see :meth:`Parser.then`.

(Hint - the arrows point at the important parser!)

.. code-block:: python

   >>> (string('x') >> string('y')).parse('xy')
   'y'


.. _parser-plus:

``+`` operator
--------------

``parser1 + parser2``

Requires both parsers to match in order, and adds the two results together using
the + operator. This will only work if the results support the plus operator
(e.g. strings and lists):


.. code-block:: python

   >>> (string("x") + regex("[0-9]")).parse("x1")
   "x1"

   >>> (string("x").many() + regex("[0-9]").map(int).many()).parse("xx123")
   ['x', 'x', 1, 2, 3]

The plus operator is a convenient shortcut for:

   >>> seq(parser1, parser2).combine(lambda a, b: a + b)

.. _parser-times:

``*`` operator
--------------

``parser1 * number``

This is a shortcut for doing :meth:`Parser.times`:

.. code-block:: python

   >>> (string("x") * 3).parse("xxx")
   ["x", "x", "x"]

You can also set both upper and lower bounds by multiplying by a range:

.. code-block:: python

   >>> (string("x") * range(0, 3)).parse("xxx")
   ParseError: expected EOF at 0:2

(Note the normal semantics of ``range`` are respected - the second number is an
*exclusive* upper bound, not inclusive).

Parser combinators
==================

.. function:: alt(*parsers)

   Creates a parser from the passed in argument list of alternative parsers,
   which are tried in order, moving to the next one if the current one fails, as
   per the :ref:`parser-or` - in other words, it matches any one of the
   alternative parsers.

   Example using `*arg` syntax to pass a list of parsers that have been
   generated by mapping :func:`string` over a list of characters:

   .. code-block:: python

      >>> hexdigit = alt(*map(string, "0123456789abcdef"))

   (In this case you would be better off using :func:`char_from`)

   Note that the order of arguments matter, as described in :ref:`parser-or`.

.. function:: seq(*parsers, **kw_parsers)

   Creates a parser that runs a sequence of parsers in order and combines
   their results in a list.


   .. code-block:: python

      >>> x_bottles_of_y_on_the_z = \
      ...    seq(regex(r"[0-9]+").map(int) << string(" bottles of "),
      ...        regex(r"\S+") << string(" on the "),
      ...        regex(r"\S+")
      ...        )
      >>> x_bottles_of_y_on_the_z.parse("99 bottles of beer on the wall")
      [99, 'beer', 'wall']


   In Python 3.6, you can also use ``seq`` with keyword arguments instead of positional
   arguments. In this case, the produced value is a dictionary of the individual
   values, rather than a sequence. This can make the produced value easier
   to consume.

   .. code-block:: python

      >>> name = seq(first_name=regex("\S+") << whitespace,
      ...            last_name=regex("\S+")
      >>> name.parse("Jane Smith")
      {'first_name': 'Jane',
       'last_name': 'Smith'}

   .. versionchanged:: 1.1
      Added ``**kwargs`` option.

   .. note::
      The ``**kwargs`` feature is for Python 3.6 and later only, because keyword
      arguments do not keep their order in earlier versions.

      For earlier versions, see :meth:`Parser.tag` for a way of labelling parsed
      components and producing dictionaries.


Other combinators
=================

Parsy does not try to include every possible combinator - there is no reason why
you cannot create your own for your needs using the built-in combinators and
primitives. If you find something that is very generic and would be very useful
to have as a built-in, please :doc:`submit </contributing>` as a PR!
