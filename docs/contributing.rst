Contributing to parsy
=====================

Contributions to parsy, whether code or docs, are very welcome. Please
contribute by making a fork, and submitting a PR on `GitHub
<https://github.com/python-parsy/parsy>`_.

All contributions will need to be fully covered by unit tests and documentation.
Code should be formatted according to pep8, and the formatting defined by
the ``../.editorconfig`` file.

To run the test suite::

    pip install pytest
    pytest

To run the test suite on all supported Python versions, first install the
various Python versions, then::

    pip install tox
    tox

To build the docs, do::

    pip install sphinx
    cd docs
    make html

We also require that flake8, isort and checkmanifest report zero errors (these
are run by tox).

When writing documentation, please keep in mind Daniele Procida's `great article
on documentation <https://www.divio.com/en/blog/documentation/>`_. To summarise,
there are 4 types of docs:

* Tutorials
* How-to guides
* Discussions
* Reference

We do not (yet) have documentation that fits into the "Discussions" category,
but we do have the others, and when adding new features, documentation of the
right sort(s) should be added.
