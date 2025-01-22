#!/bin/sh

pytest || exit 1
pre-commit run --all --all-files || exit 1

umask 000
rm -rf build dist
git ls-tree --full-tree --name-only -r HEAD | xargs chmod ugo+r

uv build --sdist --wheel || exit 1
uv publish  || exit 1

VERSION=$(uv pip show parsy | grep 'Version: ' | cut -f 2 -d ' ' | tr -d '\n') || exit 1

git tag v$VERSION || exit 1
git push || exit 1
git push --tags || exit 1
