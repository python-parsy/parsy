==================
How to do releases
==================

* Check test suite passes on all supported versions::

    tox

* Change docs/history.rst to remove " - unreleased"

* Update the version number (removing the ``-dev1`` part):

  * src/parsy/version.py
  * docs/conf.py

* Commit with "Version bump"

* Release to PyPI::

    $ VERSION=$(./setup.py --version)

    $ ./setup.py sdist bdist_wheel

    $ twine upload dist/parsy-$VERSION-py2.py3-none-any.whl dist/parsy-$VERSION.tar.gz

* Tag and push::


    git tag v$VERSION
    git push
    git push --tags


Post release
------------

* Bump version numbers to next version, and add ``-dev1`` suffix, for example
  ``0.9.0-dev1``

* Add new section to docs/history.rst, with " - unreleased".

* Commit and push
