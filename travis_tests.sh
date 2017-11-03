#!/usr/bin/env bash

coverage run --branch --source=parsy `which py.test` || exit 1

codecov
