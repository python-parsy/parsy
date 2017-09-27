========
Overview
========

Parsy is an easy way to combine simple, small parsers into complex, larger
parsers.

If it means anything to you, it's a monadic parser combinator library for
LL(infinity) grammars in the spirit of Parsec, Parsnip, and Parsimmon.

If that means nothing, rest assured that parsy is a very straightforward and
Pythonic solution for parsing text that doesn't require knowing anything about
monads.

parsy differentiates itself from other solutions with the following:

* a very clean implementation, only a few hundred lines.
* free, good quality documentation, all in one place. (Please raise an issue on
  GitHub if you have any problems, or find the documentation lacking in any
  way).
* it avoids mutability, and therefore a ton of related bugs.
* it has monadic binding with a :doc:`nice syntax </generating>`. In plain
  English:

  * we can easily handle cases where later parsing depends on the value of
    something parsed earlier e.g. Hollerith constants.
  * it's easy to build up complex result objects, rather than having list of
    lists etc.
  * there is no need for things like `pyparsing's Forward class
    <http://infohost.nmt.edu/tcc/help/pubs/pyparsing/web/class-Forward.html>`_ .

* it has a minimalist philopsophy. It doesn't include builtin helpers for any
  specific grammars or languages, but provides building blocks for making these.

Basic usage looks like this:

.. code-block:: python

   >>> from parsy import string
   >>> parser = (string('Dr.') | string('Mr.') | string('Mrs.')).desc("title")
   >>> parser.parse('Mrs.')
   'Mrs.'
   >>> parser.parse('Mr.')
   'Mr.'

   >>> parser.parse('Joe')
   ParseError: expected title at 0:0

   >>> parser.parse_partial('Dr. Who')
   ('Dr.', ' Who')

To learn how to use parsy, you should continue with:

* the :doc:`tutorial </tutorial>`, especially if you are not familiar with this
  type of parser library.
* the :doc:`parser generator decorator </generating>`
* the :doc:`builtin parser primitives </primitives>`
* the :doc:`method reference </methods_and_combinators>`
