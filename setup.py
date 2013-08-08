#!/usr/bin/env python

# http://svn.python.org/projects/sandbox/trunk/setuptools/setuptools.txt

from setuptools import setup

import phantomcurl.version as version

with open('README.md') as h:
    long_description = h.read()

setup(
    name='phantomcurl',
    version=version.current,
    description='Thin wrapper around PhantomJS',
    long_description=long_description,
    author='Jakub Mikians',
    author_email='jakub.mikians@gmail.com',
    packages=['phantomcurl'],
    package_data={'': ['*.js', 'README.md']},
    install_requires=[],
    #scripts=['phantomcurl/phantomcurl'], install executable scripts
)
