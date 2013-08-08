phantomcurl
===========

Python wrapper around PhantomJS headless borwser

Instalation
===========

Build and install the egg:

    make
    easy_install dist/phantomcurl-XXXX-py2.7.egg

Install PhantomJS binary from http://phantomjs.org/. For Mac OS it would be:
    
    https://phantomjs.googlecode.com/files/phantomjs-1.9.0-macosx.zip

phantomjs should be visible system wise:

    which phantomjs

Otherwise, you can export an environment variable PHANTOMJS_BIN to point to the
PhantomJS binary


Returned values
===============

`fetch()` returns dictionary with the following fields:

    url             - URL feeded to the fetch function
    requests        - all requests captured
    responses       - all responses captured
    content         - content of the webpage
    timestamps      - [start, end], seconds
    version         - version of the JS script
    command_line    - command line arguments passed to the JS 


IFrames inspection
==================

The script allows deep iframes inspection (-f option). For each iframe it reports `src`, `id` and its content. Then for each frame it check if it contains more iframes and reports them, recursively.


Redirections
============

Suitable to follow redirections, if redirection is realised as JavaScript or form

Command line tool
================

You can use the script as a commandline tool with:

    python -mphantomcurl --help

Returns data in JSON format


