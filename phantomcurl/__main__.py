#!/usr/bin/env python2.7

import sys
import os
import argparse
import logging
import json
import codecs

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from phantomcurl.core import PhantomCurl, PhantomCurlError
from phantomcurl.utils import logger
import phantomcurl.helpstrings
import phantomcurl.version as version


USER_AGENT = (u'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 '
              u'(KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31')


def get_options():
    p = argparse.ArgumentParser(
        prog='python -m phantomcurl',
        description=phantomcurl.helpstrings.description,
        epilog=phantomcurl.helpstrings.epilog,
        formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument('url', nargs='?')
    p.add_argument('-A', '--user-agent', default=USER_AGENT,
                   metavar='<user_agent>')
    p.add_argument('-c', '--cookie-jar', metavar='<path>',
                   help='file with permanent cookies')
    p.add_argument('-d', '--delay', metavar='<sec>', type=float,
                   help='wait additional X seonds')
    p.add_argument('-f', '--inspect-iframes', default=False,
                   action='store_true', help='inspect iframes recursively')
    p.add_argument('-L', '--landing-page', default=False, action='store_true',
                   help='presets suitable for capturing the landing page only')
    p.add_argument('-m', '--dump-content', default=False,
                   action='store_true')
    p.add_argument('-N', '--no-content', dest='with_content', default=True,
                   action='store_false', help='do not return page source')
    p.add_argument('-o', '--output', metavar='<path>',
                   help='output file')
    p.add_argument('-p', '--post', nargs='*', action='append',
                   metavar='key [value]',
                   help='send POST with data')
    p.add_argument('-r', '--with-request-response', default=False,
                   action='store_true', help='capture requests and responses')
    p.add_argument('-s', '--capture-screen', metavar='<filename>')
    p.add_argument('-t', '--timeout', metavar='<sec>', type=float,
                   help='timeout for whole operation')
    p.add_argument('-x', '--proxy', metavar='<address>',
                   help='HTTP proxy address')
    p.add_argument('-V', '--version', default=False,
                   action='store_true')
    p.add_argument('--debug', default=False,
                   action='store_true')

    opts = p.parse_args()
    if not opts.version and not opts.url:
        print 'Missing URL'
        p.print_usage()
        sys.exit(-1)
    if opts.landing_page:
        opts.dump_content = False
        opts.capture_screen = None
        opts.inspect_iframes = False
        opts.timeout = 30.0
        opts.delay = 1.0
        opts.with_content = False
        opts.with_request_response = False
    return opts


def die(message):
    print 'Error: {}'.format(message)
    sys.exit(-1)


def set_logging():
    stream_err = logging.StreamHandler(sys.stderr)
    logger.addHandler(stream_err)
    logger.setLevel(logging.DEBUG)


def print_err(message):
    sys.stderr.write(str(message) + "\n")


def valid_post_data_pairs(items):
    valid_pairs = []
    for item in items:
        if not item:
            pass
        elif 1 == len(item):
            valid_pairs.append((item[0], ''))
        elif 2 == len(item):
            valid_pairs.append(tuple(item))
        else:
            raise ValueError(item)
    return valid_pairs


def main():
    set_logging()
    opts = get_options()
    if opts.version:
        print version.current
        sys.exit(0)
    post_params = (None if opts.post is None
                   else valid_post_data_pairs(opts.post))
    pjs = PhantomCurl(cookie_jar=opts.cookie_jar,
                      user_agent=opts.user_agent,
                      proxy=opts.proxy,
                      inspect_iframes=opts.inspect_iframes,
                      timeout_sec=opts.timeout,
                      debug=opts.debug,
                      delay=opts.delay,
                      with_content=opts.with_content,
                      with_request_response=opts.with_request_response)
    try:
        page = pjs.fetch(opts.url,
                         post_params=post_params,
                         capture_screen=opts.capture_screen)
    except PhantomCurlError as exc:
        print_err('!!!ERROR: {}'.format(exc.__class__.__name__))
        print_err(exc)
        for err_out in (m for m in [exc.out, exc.err] if m is not None):
            print_err(err_out)
        sys.exit(1)
    pretty_output = (page['content'] if opts.dump_content else
                     json.dumps(page, indent=1))
    with (codecs.open(opts.output, 'w', encoding='utf8') if opts.output
          else sys.stdout) as out_stream:
        out_stream.write(pretty_output)

if __name__ == "__main__":
    main()
