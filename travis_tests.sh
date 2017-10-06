#!/usr/bin/env sh

coverage run --branch --source=parsy `which py.test` && coveralls
