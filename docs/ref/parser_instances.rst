=============================
Creating new Parser instances
=============================

.. currentmodule:: parsy

Normally you will create Parser instances using the provided :doc:`primitives
</ref/primitives>` and :doc:`combinators </ref/methods_and_combinators>`.

However it is also possible to create them manually, as below.

The :class:`Parser` constructor should be passed a function that takes the
string/list to be parsed and an index into that string, and returns a
:class:`Result` object. The ``Result`` object will be created either using
:meth:`Result.success` or :meth:`Result.failure` to indicate success or failure
respectively. :meth:`Result.success` should be passed the next index to continue
parsing with, and the value that is returned from the parsing.
:meth:`Result.failure` should return the index at which failure occurred i.e.
the index passed in, and a string indicating what the parser expected to find.

The ``Parser`` constructor will usually be called using decorator syntax. In
order to pass parameters to the ``Parser`` instance, it is typically created
using a closure. In the example below, we create a parser that matches any
string/list of tokens of a given length. This could also be written as something
like ``any_char.times(n).concat()`` but the following will be more efficient:


.. code-block:: python

   def consume(n):

       @Parser
       def consumer(stream, index):
           items = stream[index:index + n]
           if len(items) == n:
               return Result.success(index + n, items)
           else:
               return Result.failure(index, "{0} items".format(n))

       return consumer


.. code-block:: python

   >>> consume(3).many().parse('abc123def')
   ['abc', '123', 'def']


Result objects
==============

.. class:: Result

   .. staticmethod:: success(next_index, value)

      Creates a ``Result`` object indicating parsing succeeded. The index to
      continue parsing at, and the value retrieved from the parsing, should be
      passed.

   .. staticmethod:: failure(index, expected)

      Creates a ``Result`` object indicating parsing failed. The index to
      continue parsing at, and a string representing what the parser expected to
      find, should be passed.
