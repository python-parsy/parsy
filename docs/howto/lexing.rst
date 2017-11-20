=====================================
 Separate lexing/tokenization phases
=====================================

.. currentmodule:: parsy

Most of the documentation in parsy assumes that when you call
:meth:`Parser.parse` you will pass a string, and will get back your final
parsed, constructed object (of whatever type you desire).

A more classical approach to parsing is that you first have a
lexing/tokenization phase, the result of which is a simple list of tokens. These
tokens could be strings, or other objects.

You then have a separate parsing phase that consumes this list of tokens, and
produces your final object, which is very often a tree-like structure or other
complex object.

Parsy can actually work with either approach. Further, for the split
lexing/parsing approach, parsy can be used either to implement the lexer, or the
parser, or both! The following examples use parsy to do both lexing and parsing.

However, parsy's features for this use case are not as developed as some other
Python tools. If you are building a parser for a full language that needs the
split lexing/parsing approach, you might be better off with `PLY
<http://www.dabeaz.com/ply/>`_.

Turtle Logo
===========

For our first example, we'll do a very stripped down Turtle Logo parser. First,
the lexer:

.. literalinclude:: ../../examples/simple_logo_lexer.py
   :language: python


We are not interested in whitespace, so our lexer removes it all, apart from
newlines. We can now parse a program into the tokens we are interested in:

.. code-block:: python

   >>> l = lexer.parse("fd 1\nbk 2")
   >>> l
   ['fd', 1, '\n', 'bk', 2, '\n']

The ``line`` parser produces a list, so after applying ``many`` which also
produces a list, we applied a level of flattening so that we end up with a
simple list of tokens. We also chose to convert the parameters to integers while
we were at it, so in this case our list of tokens is not a list of strings, but
heterogeneous.

The next step is the parser. We create some classes to represent different
commands, and then use parsy again to create a parser which is very simple
because this is a very limited language:

.. literalinclude:: ../../examples/simple_logo_parser.py
   :language: python

To use it, we pass the the list of tokens generated above into
``program.parse``:

.. code-block:: python

   >>> program.parse(l)
   [Forward(1), Backward(2)]

In a real implementation, we could then have ``execute`` methods on the
``Command`` sub-classes if we wanted to implement an interpreter, for example.

Calculator
==========

Our second example illustrates lexing and then parsing a sequence of
mathematical operations, e.g "1 + 2 * (3 - 4.5)", with precedence.

In this case, while doing the parsing stage, instead of building up an AST of
objects representing the operations, the parser actually evaluates the
expression.

.. literalinclude:: ../../examples/simple_eval.py
   :language: python
