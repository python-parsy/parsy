========
Tutorial
========

.. currentmodule:: parsy

First :doc:`install parsy </installation>`, and check that the documentation you
are reading matches the version you just installed.

Building an ISO 8601 parser
===========================

In this tutorial, we are going to gradually build a parser for a subset of an
ISO 8601 date. Specifically, we want to handle dates that look like this:
``2017-09-25``.

A problem of this size could admittedly be solved fairly easily with regexes.
But very quickly regexes don't scale, especially when it comes to getting the
parsed data out, and for this tutorial we need to start with a simple example.

With parsy, you start by breaking the problem down into the smallest components.
So we need first to match the 4 digit year at the beginning.

There are various ways we can do this, but a regex works nicely, and
:func:`regex` is a built-in primitive of the parsy library:

.. code-block:: python

   >>> from parsy import regex
   >>> year = regex(r'[0-9]{4}')

(For those who don't know regular expressions, the regex ``[0-9]{4}`` means
“match any character from 0123456789 exactly 4 times”.)

This has produced a :class:`Parser` object which has various methods. We can
immediately check that it works using the :meth:`Parser.parse` method:

.. code-block:: python

   >>> year.parse('2017')
   '2017'
   >>> year.parse('abc')
   ParseError: expected '[0-9]{4}' at 0:0

Notice first of all that a parser consumes input (the value we pass to
``parse``), and it produces an output. In the case of ``regex``, the produced
output is the string that was matched, but this doesn't have to be the case for
all parsers.

If there is no match, it raises a ``ParseError``.

Notice as well that the :meth:`Parser.parse` method expects to consume all the
input, so if there are extra characters at the end, even if it is just
whitespace, parsing will fail with a message saying it expected EOF (End Of
File/Data):

.. code-block:: python

   >>> year.parse('2017 ')
   ParseError: expected 'EOF' at 0:4

You can use :meth:`Parser.parse_partial` if you want to just keep parsing as far
as possible and not throw an exception.

To parse the data, we need to parse months, days, and the dash symbol, so we'll
add those:

.. code-block:: python

   >>> from parsy import string
   >>> month = regex('[0-9]{2}')
   >>> day = regex('[0-9]{2}')
   >>> dash = string('-')

We've added use of the :func:`string` primitive here, that matches just the
string passed in, and returns that string.

Next we need to combine these parsers into something that will parse the whole
date. The simplest way is to use the :meth:`Parser.then` method:

.. code-block:: python

   >>> fulldate = year.then(dash).then(month).then(dash).then(day)

The ``then`` method returns a new parser that requires the first parser to
succeed, followed by the second parser (the argument to the method).

We could also write this using the :ref:`parser-rshift` which
does the same thing as :meth:`Parser.then`:

.. code-block:: python

   >>> fulldate = year >> dash >> month >> dash >> day

This parser has some problems which we need to address, but it is already useful
as a basic validator:

.. code-block:: python

   >>> fulldate.parse('2017-xx')
   ParseError: expected '[0-9]{2}' at 0:5
   >>> fulldate.parse('2017-01')
   ParseError: expected '-' at 0:7
   >>> fulldate.parse('2017-02-01')
   '01'

If the parse doesn't succeed, we'll get ``ParseError``, otherwise it is valid
(at least as far as the basic syntax checks we've added).

The first problem with this parser is that it doesn't return a very useful
value. Due to the way that :meth:`Parser.then` works, when it combines two
parsers to produce a larger one, the value from the first parser is discarded,
and the value returned by the second parser is the overall return value. So, we
end up getting only the 'day' component as the result of our parse. We really
want the year, month and day packaged up nicely, and converted to integers.

A second problem is that our error messages are not very friendly.

Our first attempt at fixing these might be to use the :ref:`parser-plus` instead
of ``then``. This operator is defined to combine the results of the two parsers
using the normal plus operator, which will work fine on strings:

   >>> fulldate = year + dash + month + dash + day
   >>> fulldate.parse('2017-02-01')
   '2017-02-01'

However, it won't help us if we want to split our data up into a set of
integers.

Our first step should actually be to work on the year, month and day components
using :meth:`Parser.map`, which allows us to convert the strings to other
objects - in our case we want integers.

We can also use the :meth:`Parser.desc` method to give nicer error messages, so
our components now look this this:

.. code-block:: python

   >>> year = regex('[0-9]{4}').map(int).desc('4 digit year')
   >>> month = regex('[0-9]{2}').map(int).desc('2 digit month')
   >>> day = regex('[0-9]{2}').map(int).desc('2 digit day')

We get better error messages now:

.. code-block:: python

   >>> year.then(dash).then(month).parse('2017-xx')
   ParseError: expected '2 digit month' at 0:5


Notice that the ``map`` and ``desc`` methods, like all similar methods on
``Parser``, return new parser objects - they do not modify the existing one.
This allows us to build up parsers with a 'fluent' interface, and avoid problems
caused by mutating objects.

However, we still need a way to package up the year, month and day as separate
values.

The :func:`seq` combinator provides one easy way to do that. It takes the
parsers that are passed in as arguments, and combines their results into a
list:

.. code-block:: python

   >>> fulldate = seq(year, dash, month, dash, day)
   >>> fulldate.parse('2017-01-02')
   [2017, '-', 1, '-', 2]

Now, we don't need those dashes, so we can eliminate them using the :ref:`parser-rshift` or :ref:`parser-lshift`:

.. code-block:: python

   >>> fulldate = seq(year, dash >> month, dash >> day)
   >>> fulldate.parse('2017-01-02')
   [2017, 1, 2]

At this point, we could also convert this to a date object if we wanted using
:meth:`Parser.combine`:

.. code-block:: python

   >>> from datetime import date
   >>> fulldate = seq(year, dash >> month, dash >> day).combine(date)

We could have used :meth:`Parser.map` here, but :meth:`Parser.combine` is a bit
nicer. It's especially succinct because the argument order to ``date`` matches
the order of the values parsed (year, month, day), otherwise we could have
passed a ``lambda`` to ``combine``, or used :meth:`Parser.combine_dict`.

.. _using-previous-values:

Using previously parsed values
==============================

Now, sometimes we might want to do more complex logic with the values that are
collected as parse results, and do so while we are still parsing.

To continue our example, the above parser has a problem that it will raise an
exception if the day and month values are not valid. We'd like to be able to
check this, and produce a parse error instead, which will make our parser play
better with others if we want to use it to build something bigger.

Also, in ISO8601, strictly speaking you can just write the year, or the year and
the month, and leave off the other parts. We'd like to handle that by returning
a tuple for the result, and ``None`` for the missing data.

To do this, we need to allow the parse to continue if the later components (with
their leading dashes) are missing - that is, we need to express optional
components, and we need a way to be able to test earlier values while in the
middle of parsing, to see if we should continue looking for another component.

The :meth:`Parser.bind` method provides one way to do it (yay monads!).
Unfortunately, it gets ugly pretty fast, and in Python we don't have Haskell's
``do`` notation to tidy it up. But thankfully we can use generators and the
``yield`` keyword to great effect.

We use a generator function and convert it into a parser by using the
:func:`generate` decorator. The idea is that you ``yield`` every parser that you
want to run, and receive the result of that parser as the value of the yield
expression. You can then put parsers together using any logic you like, and
finally return the value.

An equivalent parser to the one above can be written like this:

.. code-block:: python

   @generate
   def full_date():
       y = yield year
       yield dash  # implicit skip, since we do nothing with the value
       m = yield month
       yield dash
       d = yield day
       return date(y, m, d)

This is more verbose than before, but provides a good starting point for our
next set of requirements.

First of all, we need to express optional components - that is we need to be
able to handle missing dashes, and return what we've got so far rather than
failing the whole parse.

:class:`Parser` has a set of methods that convert parsers into ones that allow
multiples of the parser - including :meth:`Parser.many`, :meth:`Parser.times`,
:meth:`Parser.at_most` and :meth:`Parser.at_least`. There is also
:meth:`Parser.optional` which allows matching zero times (in which case the
parser will return ``None``), or exactly once - just what we need in this case.

We also need to do checking on the month and the day. We'll take a shortcut and
use the built-in ``datetime.date`` class to do the validation for us. However,
rather than allow exceptions to be raised, we convert the exception into a
parsing failure.


.. code-block:: python

   optional_dash = dash.optional()

   @generate
   def full_or_partial_date():
       d = None
       m = None
       y = yield year
       dash1 = yield optional_dash
       if dash1 is not None:
           m = yield month
           dash2 = yield optional_dash
           if dash2 is not None:
                d = yield day
       if m is not None:
          if m < 1 or m > 12:
              return fail("month must be in 1..12")
       if d is not None:
          try:
              datetime.date(y, m, d)
          except ValueError as e:
              return fail(e.args[0])

       return (y, m, d)


This works now works as expected:

.. code-block:: python

   >>> full_or_partial_date.parse('2017-02')
   (2017, 2, None)
   >>> full_or_partial_date.parse('2017-02-29')
   ParseError: expected 'day is out of range for month' at 0:10

We could of course use a custom object in the final line to return a more
convenient data type, if wanted.

Alternatives and backtracking
=============================

Suppose we are using our date parser to scrape dates off articles on a web site.
We then discover that for recently published articles, instead of printing a
timestamp, they write "X days ago".

We want to parse this, and we'll use a timedelta object to represent the value
(to easily distinguish it from other values and consume it later). We can write
a parser for this easily:

.. code-block:: python

   >>> days_ago = regex("[0-9]+").map(lambda d: timedelta(days=-int(d))) << string(" days ago")
   >>> days_ago.parse("5 days ago")
   datetime.timedelta(-5)

Now we need to combine it with our date parser, and allow either to succeed.
This is done using the :ref:`parser-or`, as follows:


.. code-block:: python

   >>> flexi_date = full_or_partial_date | days_ago
   >>> flexi_date.parse('2012-01-05')
   (2012, 1, 5)
   >>> days_ago.parse("2 days ago")
   datetime.timedelta(-2)

Notice that you still get good error messages from the appropriate parser,
depending on which parser got furthest before returning a failure:

.. code-block:: python

   >>> flexi_date.parse('2012-')
   ParseError: expected '2 digit month' at 0:5
   >>> flexi_date.parse('2 years ago')
   ParseError: expected ' days ago' at 0:1

When using backtracking, you need to understand that backtracking to the other
option only occurs if the first parser fails. So, for example:

.. code-block:: python

   >>> a = string("a")
   >>> ab = string("ab")
   >>> c = string("c")
   >>> a_or_ab_and_c = ((a | ab) + c)
   >>> a_or_ab_and_c.parse('ac')
   'ac'
   >>> a_or_ab_and_c.parse('abc')
   ParseError: expected 'c' at 0:1

The parse fails because the ``a`` parser succeeds, and so the ``ab`` parser is
never tried. This is different from most regular expressions engines, where
backtracking is done over the whole regex by default.

In this case we can get the parse to succeed by switching the order:

.. code-block:: python

   >>> ((ab | a) + c).parse('abc')
   'abc'

   >>> ((ab | a) + c).parse('ac')
   'ac'

We could also fix it like this:

.. code-block:: python

   >>> ((a + c) | (ab + c)).parse('abc')
   'abc'


Custom data structures
======================

In the example shown so far, the result of parsing has been a native Python data
type, such as a integer, string, datetime or tuple. In some cases that is
enough, but very quickly you will find that for your parse result to be useful,
you will need to use custom data structures (rather than ending up with nested
lists etc.)

For defining custom data structures, you can use any method you like (e.g.
simple classes). We recommend `attrs
<https://attrs.readthedocs.io/en/stable/>`_. You can also use `namedtuple
<https://docs.python.org/3.6/library/collections.html#collections.namedtuple>`_
from the standard library for simple cases or `dataclasses
<https://docs.python.org/3/library/dataclasses.html>`_.

For combining parsed data into these data structures, you can:

1. Use :meth:`Parser.map`, :meth:`Parser.combine` and :meth:`Parser.combine_dict`,
   often in conjunction with :func:`seq`.

   See the :doc:`SQL SELECT and .proto file parser examples
   </howto/other_examples/>` for examples of this approach.

2. Use the ``@generate`` decorator as above, and manually call the data
   structure constructor with the pieces, as in ``full_date`` or
   ``full_or_partial_date`` above, but with your own data structure instead of a
   tuple or datetime in the final line.


Learn more
==========

For further topics, see the :doc:`table of contents </index>` for the rest of
the documentation that should enable you to build parsers for your needs.
