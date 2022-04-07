==============
Other examples
==============

.. currentmodule:: parsy

This section has some further example parsers that you can study. There are also
examples in the :doc:`/tutorial` and in :doc:`/ref/generating`.

SQL SELECT statement parser
===========================

This shows a very simplified parser for a SQL ``SELECT`` statement, using custom
data structures, and the convenient keyword argument syntax for :func:`seq`,
followed by :meth:`Parser.combine_dict`.

.. literalinclude:: ../../examples/sql_select.py
   :language: python


JSON parser
===========

A full parser for JSON. (This will not be competitive in terms of performance
with other implementations!)

This demonstrates the use of :class:`forward_declaration`, needed due to the
circular definition of ``json_value``.

.. literalinclude:: ../../examples/json.py
   :language: python
