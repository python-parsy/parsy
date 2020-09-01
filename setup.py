#!/usr/bin/env python

import os.path

from setuptools import find_packages, setup

# Evaluate version module without importing parsy, which could have undesirable
# effects.
version_file = os.path.join(os.path.dirname(__file__),
                            "src", "parsy", "version.py")
namespace = {}
exec(compile(open(version_file, "rb").read(), version_file, 'exec'),
     globals(), namespace)
version = namespace['__version__']

readme = open('README.rst').read()

setup(
    name="parsy",
    version=version,
    description="easy-to-use parser combinators, for parsing in pure Python",
    long_description=readme,
    author="Jeanine Adkisson",
    author_email="jneen@jneen.net",
    maintainer="Luke Plant",
    maintainer_email="L.Plant.98@cantab.net",
    url="https://github.com/python-parsy/parsy",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="parser parsers parsing monad combinators",
    packages=find_packages('src'),
    package_dir={'': 'src'},
)
