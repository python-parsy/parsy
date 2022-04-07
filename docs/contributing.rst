Contributing to parsy
=====================

Contributions to parsy, whether code or docs, are very welcome. Please
contribute by making a fork, and submitting a PR on `GitHub
<https://github.com/python-parsy/parsy>`_.

We have a high standard in terms of quality. All contributions will need to be
fully covered by unit tests and documentation.

To run the test suite::

    pip install pytest
    pytest

To run the test suite on all supported Python versions, and code quality checks,
first install the various Python versions, then::

    pip install tox
    tox

To build the docs, do::

    pip install sphinx
    cd docs
    make html

We now have several linters and code formatters that we require use of,
including `flake8 <http://flake8.pycqa.org/en/latest/>`_, `isort
<https://github.com/timothycrosley/isort#readme>`_ and `black
<https://github.com/psf/black>`_. These are most easily add by using `pre-commit
<https://pre-commit.com/>`_:

* Install pre-commit globally e.g. ``pipx install pre-commit`` if you already
  have `pipx <https://github.com/pypa/pipx>`_.

* Do ``pre-commit install`` in the repo.

Now all the linters will run when you commit changes.

When writing documentation, please keep in mind Daniele Procida's `great article
on documentation <https://www.divio.com/en/blog/documentation/>`_. To summarise,
there are 4 types of docs:

* Tutorials (focus: learning, analogy: teaching a child to cook)
* How-to guides (focus: goals, analogy: a recipe in a cook book)
* Discussions (focus: understanding, analogy: an article on culinary history)
* Reference (focus: information, analogy: encyclopedia article)

We do not (yet) have documentation that fits into the "Discussions" category,
but we do have the others, and when adding new features, documentation of the
right sort(s) should be added. With parsy, where code is often very succinct,
writing good docs often takes several times longer than writing the code.
