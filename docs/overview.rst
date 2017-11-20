========
Overview
========

Parsy is an easy way to combine simple, small parsers into complex, larger
parsers.

If it means anything to you, it's a monadic parser combinator library for
LL(infinity) grammars in the spirit of `Parsec
<https://github.com/haskell/parsec>`_, `Parsnip
<http://parsnip-parser.sourceforge.net/>`_, and `Parsimmon
<https://github.com/jneen/parsimmon>`_.

If that means nothing, rest assured that parsy is a very straightforward and
Pythonic solution for parsing text that doesn't require knowing anything about
monads.

Parsy differentiates itself from other solutions with the following:

* it is not a parser generator, but a combinator based parsing library.
* a very clean implementation, only a few hundred lines, that borrows
  from the best of recent combinator libraries.
* free, good quality documentation, all in one place. (Please raise an issue on
  GitHub if you have any problems, or find the documentation lacking in any
  way).
* it avoids mutability, and therefore a ton of related bugs.
* it has monadic binding with a :doc:`nice syntax </ref/generating>`. In plain
  English:

  * we can easily handle cases where later parsing depends on the value of
    something parsed earlier e.g. Hollerith constants.
  * it's easy to build up complex result objects, rather than returning lists of
    lists etc. which then need to be further processed.
  * there is no need for things like `pyparsing's Forward class
    <http://infohost.nmt.edu/tcc/help/pubs/pyparsing/web/class-Forward.html>`_ .

* it has a minimalist philosophy. It doesn't include built-in helpers for any
  specific grammars or languages, but provides building blocks for making these.

Basic usage looks like this:

Example 1 - parsing a set of alternatives:

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

Example 2 - Parsing a dd-mm-yy date:

.. code-block:: python

   >>> from parsy import string, regex
   >>> from datetime import date
   >>> ddmmyy = regex(r'[0-9]{2}').map(int).sep_by(string("-"), min=3, max=3).combine(
   ...                lambda d, m, y: date(2000 + y, m, d))
   >>> ddmmyy.parse('06-05-14')
   datetime.date(2014, 5, 6)


To learn how to use parsy, you should continue with:

* the :doc:`tutorial </tutorial>`, especially if you are not familiar with this
  type of parser library.
* the :doc:`parser generator decorator </ref/generating>`
* the :doc:`builtin parser primitives </ref/primitives>`
* the :doc:`method and combinator reference </ref/methods_and_combinators>`

Other Python projects
=====================

* `pyparsing <http://pyparsing.wikispaces.com/>`_. Also a combinator approach,
  but in general much less cleanly implemented, and rather scattered
  documentation, although it has more builtin functionality in terms
  of provided utilities for certain parsing tasks.

* `PLY <http://www.dabeaz.com/ply/>`_. A pure Python implementation of
  the classic lex/yacc parsing tools. It is well suited to large grammars
  that would be found in typical programming languages.

* `funcparserlib <https://github.com/vlasovskikh/funcparserlib>`_ - the most
  similar to parsy. It differs from parsy mainly in normally using a separate
  tokenization phase, lacking the convenience of the :func:`generate` method for
  creating parsers, and documentation that relies on understanding Haskell type
  annotations.

* `Lark <https://github.com/erezsh/lark>`_. With Lark you write a grammar
  definition in a separate mini-language as a string, and have a parser
  generated for you, rather than writing the grammar in Python. It has the
  advantage of speed and being able to use different parsing algorithms.
