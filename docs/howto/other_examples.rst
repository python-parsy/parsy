==============
Other examples
==============

.. currentmodule:: parsy

This section has some further example parsers that you can study. There are also
examples in the :doc:`/tutorial` and in :doc:`/ref/generating`.

SQL SELECT statement parser
===========================

This shows a very simplified parser for a SQL ``SELECT`` statement, using custom
data structures, and the convenient keyword argument syntax for :func:`seq`
(usable with Python 3.6 and later), followed by :meth:`Parser.combine_dict`.

.. literalinclude:: ../../examples/sql_select.py
   :language: python


JSON parser
===========

A full parser for JSON. (This will not be competitive in terms of performance
with other implementations!)

.. literalinclude:: ../../examples/json.py
   :language: python

.proto file parser
==================

A parser for the ``.proto`` files for Protocol Buffers, version 3.

This example is useful in showing lots of simple custom data structures for
holding the result of the parse. It uses the :meth:`Parser.tag` method
for labelling parts, followed by :meth:`Parser.combine_dict`.

.. literalinclude:: ../../examples/proto3.py
   :language: python
