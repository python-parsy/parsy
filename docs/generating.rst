===================
Generating a parser
===================

.. currentmodule:: parsy
.. function:: generate

Constructing parsers by using combinators and :class:`Parser` methods to make
larger parsers works well for many simpler cases. However, for more complex
caseses the ``generate`` function decorator is both more readable and more powerful.

``parsy.generate`` creates a parser from a generator function that should yield
parsers. These parsers are applied successively and their results are sent back
to the generator using the ``.send()`` protocol. The generator should return the
final result of the parsing. Alternatively it can return another parser, which
is equivalent to applying it and returning its result.

The first example just shows a different way of building a parser that could
have easily been using combinators:

.. code:: python

   from parsy import generate

   @generate
   def form():
       """
       Parse an s-expression form, like (a b c).
       An equivalent to lparen >> expr.many() << rparen
       """
       yield lparen
       exprs = yield expr.many()
       yield rparen
       return exprs


Note that there is no guarantee that the entire function is executed: if
any of the yielded parsers fails, parsy will try to backtrack to an
alternative parser if there is one.

The second example shows how you can use multiple parse results to build up a
complex object:

.. code:: python

   from datetime import date

   from parsy import generate

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

The third example shows how we can use an earlier parsed value to influence the
subsequent parsing. This example parses Hollerith constants. Holerith constants
are a way of specifying an arbitrary set of characters by first writing the
integer that specifies the length, followed by the character H, followed by the
set of characters. For example, ``pancakes`` would be written ``8Hpancakes``.

.. code:: python

   from parsy import generate

   @generate
   def hollerith():
       num = yield regex(r'[0-9]+').map(int)
       yield string('H')
       val = yield regex(".").times(num)
       return ''.join(val)

(You may want to compare this with an `implementation of Hollerith constants
<https://gist.github.com/spookylukey/591aa8a6a9af7cf0f1e22129b29288d6>`_ that
uses `pyparsing <http://pyparsing.wikispaces.com/>`_, originally by John
Shipman from his `pyparsing docs
<http://infohost.nmt.edu/tcc/help/pubs/pyparsing/web/class-Forward.html>`_.)

