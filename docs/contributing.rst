Contributing to parsy
=====================

Please contribute by making a fork, and submitting a PR on `GitHub
<https://github.com/python-parsy/parsy>`_.

All contributions will need to be fully covered by unit tests and documentation.

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
