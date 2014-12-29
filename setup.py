#!/usr/bin/env python

from setuptools import setup, find_packages

from os.path import join, dirname
import sys
sys.path.insert(0, join(dirname(__file__), 'src'))
from parsy.version import __version__
sys.path.pop(0)

setup(
    name="parsy",
    version=__version__,
    description="easy-to-use parser combinators",
    author="Jeanine Adkisson",
    url="https://github.com/jneen/parsy",
    author_email="jneen at jneen dot net (humans only, please)",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="parser parsing monad combinators",
    packages=find_packages('src'),
    package_dir={'': 'src'},
)
