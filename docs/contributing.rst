Contributing to parsy
=====================

Contributions to parsy, whether code or docs, are very welcome. Please
contribute by making a fork, and submitting a PR on `GitHub
<https://github.com/python-parsy/parsy>`_.

We have a high standard in terms of quality. All contributions will need to be
fully covered by unit tests and documentation.

To get started you’ll need to:

- Check out the repo using git, ``cd`` into the directory.

- Set up a venv for development. We use `uv <https://docs.astral.sh/uv/>`_ and
  recommend you do the same. With uv, the setup instructions are::

    uv sync

  This will use your default Python version. If you want to use a different
  Python version, instead of the above do this e.g.::

    uv python install 3.10
    uv venv --python 3.10
    uv sync

- Activate the venv::

    source .venv/bin/activate

  (Alternatively, you can add ``uv run`` before most of the commands below)

- Get test suite running::

    pytest

- Run tests against all versions::

    tox

- To build the docs, do::

    cd docs
    make html

We now have several linters and code formatters that we require use of,
including `flake8 <http://flake8.pycqa.org/en/latest/>`_, `isort
<https://github.com/timothycrosley/isort#readme>`_ and `black
<https://github.com/psf/black>`_. These are most easily add by using `pre-commit
<https://pre-commit.com/>`_:

- Install `pre-commit <https://pre-commit.com/>`_ in the repo::

    pre-commit install

  This will add Git hooks to run linters when committing, which ensures our style
  (black) and other things.

  Now all the linters will run when you commit changes.

- You can also manually run these linters using::

    pre-commit run --all --all-files


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
