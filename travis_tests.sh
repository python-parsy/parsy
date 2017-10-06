#!/usr/bin/env sh

coverage run --branch --source=parsy `which py.test` || exit 1

# Coveralls is flaky sometimes, especially for concurrent uploads.
# https://github.com/lemurheavy/coveralls-public/issues/487
# So try again if it fails first time.
coveralls || { sleep $((RANDOM / 4000 + 1)); coveralls }
