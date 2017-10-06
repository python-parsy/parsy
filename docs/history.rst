=========================
History and release notes
=========================

.. currentmodule:: parsy

1.0.0 - unreleased
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

0.9.0 - 2017-09-28
------------------

* Better error reporting of failed parses.
* Documentation overhaul and expansion.
* Added :meth:`Parser.combine`.

0.0.4 - 2014-12-28
------------------

* See git logs for changes before this point.
