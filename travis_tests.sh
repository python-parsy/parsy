#!/usr/bin/env sh

coverage run --source=parsy `which py.test` && coveralls
