===================
Generating a parser
===================

.. currentmodule:: parsy
.. function:: generate

``generate`` converts a generator function (one that uses the ``yield`` keyword)
into a parser. The generator function must yield parsers. These parsers are
applied successively and their results are sent back to the generator using the
``.send()`` protocol. The generator function should return the final result of
the parsing. Alternatively it can return another parser, which is equivalent to
applying it and returning its result.

Motivation and examples
=======================

Constructing parsers by using combinators and :class:`Parser` methods to make
larger parsers works well for many simpler cases. However, for more complex
cases the ``generate`` function decorator is both more readable and more
powerful. (For those coming from Haskell/Parsec, this method provides an
acceptable substitute for ``do`` notation).

Alternative syntax to combinators
---------------------------------

The first example just shows a different way of building a parser that could
have easily been built using combinators:

.. code:: python

   from parsy import generate

   @generate("form")
   def form():
       """
       Parse an s-expression form, like (a b c).
       An equivalent to lparen >> expr.many() << rparen
       """
       yield lparen
       exprs = yield expr.many()
       yield rparen
       return exprs

In the example above, the parser was given a string name ``"form"``, which does
the same as :meth:`Parser.desc`. This is not required, as per the examples below.

Note that there is no guarantee that the entire function is executed: if any of
the yielded parsers fails, the function will not complete, and parsy will try to
backtrack to an alternative parser if there is one.

Building complex objects
------------------------

The second example shows how you can use multiple parse results to build up a
complex object:

.. code:: python

   from datetime import date

   from parsy import generate, regex, string

   @generate
   def date():
       """
       Parse a date in the format YYYY-MM-DD
       """
       year = yield regex("[0-9]{4}").map(int)
       yield string("-")
       month = yield regex("[0-9]{2}").map(int)
       yield string("-")
       day = yield regex("[0-9]{2}").map(int)

       return date(year, month, day)

This could also have been achieved using :func:`seq` and :meth:`Parser.combine`.

Using values already parsed
---------------------------

The third example shows how we can use an earlier parsed value to influence the
subsequent parsing. This example parses Hollerith constants. Hollerith constants
are a way of specifying an arbitrary set of characters by first writing the
integer that specifies the length, followed by the character H, followed by the
set of characters. For example, ``pancakes`` would be written ``8Hpancakes``.

.. code:: python

   from parsy import generate, regex, string, any_char

   @generate
   def hollerith():
       num = yield regex(r'[0-9]+').map(int)
       yield string('H')
       return any_char.times(num).concat()

(You may want to compare this with an `implementation of Hollerith constants
<https://gist.github.com/spookylukey/591aa8a6a9af7cf0f1e22129b29288d6>`_ that
uses `pyparsing <http://pyparsing.wikispaces.com/>`_, originally by John
Shipman from his `pyparsing docs
<http://infohost.nmt.edu/tcc/help/pubs/pyparsing/web/class-Forward.html>`_.)

There are also more complex examples in the :ref:`tutorial
<using-previous-values>` of using the ``generate`` decorator to create parsers
where there is logic that is conditional upon earlier parsed values.

Implementing recursive definitions
----------------------------------

A fourth examples shows how you can use this syntax for grammars that you would
like to define recursively (or mutually recursively).

Say we want to be able to pass an s-expression like syntax which uses
parenthesis for grouping items into a tree structure, like the following::

     (0 1 (2 3) (4 5 6) 7 8)

A naive approach would be:

.. code-block:: python

   simple = regex('[0-9]+').map(int)
   group = string('(') >> expr.sep_by(string(' ')) << string(')')
   expr = simple | group

The problem is that the second line will get a ``NameError`` because ``expr`` is
not defined yet.

Using the ``@generate`` syntax will introduce a level of laziness in resolving
``expr`` that allows things to work:

.. code-block:: python

   simple = regex('[0-9]+').map(int)

   @generate
   def group():
       return (yield string('(') >> expr.sep_by(string(' ')) << string(')'))

   expr = simple | group

.. code-block:: python

   >>> expr.parse("(0 1 (2 3) (4 5 6) 7 8)")
   [0, 1, [2, 3], [4, 5, 6], 7, 8]
