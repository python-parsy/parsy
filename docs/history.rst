=========================
History and release notes
=========================

.. currentmodule:: parsy

1.3.0 - 2019-08-03
------------------

* Documentation improvements.
* Added :func:`peek` - thanks `@lisael <https://github.com/lisael>`_.
* Removed Python 3.3 support
* Added Python 3.7 support
* :meth:`Parser.combine_dict` now strips keys that start with ``_``.


1.2.0 - 2017-11-15
------------------

* Added ``transform`` argument to :func:`string` and :func:`string_from`.
* Made :meth:`Parser.combine_dict` accept lists of name value pairs,
  and filter out keys with value ``None``.
* Added :func:`from_enum`.


1.1.0 - 2017-11-05
------------------

* Added :meth:`Parser.optional`.
* Added :meth:`Parser.tag`.
* Added :func:`seq` keyword argument version (Python 3.6)
* Added :meth:`Parser.combine_dict`.
* Documented :meth:`Parser.mark`.
* Documentation improvements.


1.0.0 - 2017-10-10
------------------

* Improved parse failure messages of ``@generate`` parsers. Previously
  the parser was given a default description of the function name,
  which hides all useful internal info there might be.
* Added :meth:`Parser.sep_by`
* Added :func:`test_char`
* Added :func:`char_from`
* Added :func:`string_from`
* Added :data:`any_char`
* Added :data:`decimal_digit`
* Added :meth:`Parser.concat`
* Fixed parsy so that it can again work with tokens as well as strings, allowing it to
  be used as both a :doc:`lexer or parser or both <howto/lexing>`, with docs and tests.
* Added :func:`test_item`
* Added :func:`match_item`
* Added :meth:`Parser.should_fail`

0.9.0 - 2017-09-28
------------------

* Better error reporting of failed parses.
* Documentation overhaul and expansion.
* Added :meth:`Parser.combine`.

0.0.4 - 2014-12-28
------------------

* See git logs for changes before this point.
