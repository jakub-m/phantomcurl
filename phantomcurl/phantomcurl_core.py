import json
import os
import re
import urllib

from phantomcurl.utils import logger
import phantomcurl.command as command

# 'bin/phantomjs-1.9.0-macosx/bin/phantomjs'
ENV_PHANTOMJS_BIN   = 'PHANTOMJS_BIN'
PHANTOMJS_BIN       = os.getenv(ENV_PHANTOMJS_BIN, 'phantomjs') 
_MY_DIR             = os.path.dirname(os.path.abspath(__file__))
PHANTOMJS_JS        = os.path.join(_MY_DIR, 'phantomcurl.js')

# must be the same as in .js script
_OPT_URL                 = '--url'
_OPT_USER_AGENT          = '--user-agent'
_OPT_MAGIC_STRING        = '--magic-string'
_OPT_CAPTURE_SCREEN      = '--capture-screen'
_OPT_INSPECT_IFRAMES     = '--inspect-iframes'
_OPT_TIMEOUT_SEC         = '--timeout-sec'
_OPT_DELAY_SEC           = '--delay-sec'
_OPT_NO_CONTENT          = '--no-content'
_OPT_REQUEST_RESPONSE    = '--request-response'
_OPT_POST_FULL           = '--post-full'


_MAGIC_STRING = 'MAGIC_8SD6ADEADBEEFD8AA8DS68F8_MAGIC'


POST_DATA_ITEM_RE = re.compile(r'([^=].+?)=(.*)')


class PhantomCurlError(Exception):
    def __init__(self, message, out=None, err=None, *args, **kwargs):
        super(PhantomCurlError, self).__init__(self, message, *args, **kwargs)
        self.out = out
        self.err = err


class PhantomCurl(object):
    TIMEOUT_JS_TO_JOIN_DELTA_SEC = 30.0

    def __init__(self, user_agent=None, cookie_jar=None,
                 proxy=None, timeout_sec=None,
                 inspect_iframes=False, debug=False, delay=None,
                 with_content=True, with_request_response=False,
                 post_params=None):
        '''timeout - seconds or None. If set, then phantomjs javascript timeout
        is set to this value, and thread.join timeout is set
        TIMEOUT_JS_TO_JOIN_DELTA_SEC seconds later.'''
        assert timeout_sec is None or isinstance(timeout_sec, (int, float))
        if cookie_jar and not is_writeable(cookie_jar):
            raise PhantomCurlError('Cannot write to "{}"'.format(cookie_jar))
        self._cookie_jar = cookie_jar
        self._debug = debug
        self._delay = delay
        self._inspect_iframes = inspect_iframes
        self._magic_string = _MAGIC_STRING
        self._proxy = proxy
        self._timeout_sec = timeout_sec
        self._user_agent = user_agent
        self._with_content = with_content
        self._with_request_response = with_request_response
        self._post_params = post_params

    def fetch(self, url, capture_screen=None):
        '''Return dictionary with requests, responses and content. Can raise
        PhantomCurlError with out and err values set. Will raise it when URL
        does not have a proper protocol (http or https)'''
        if not _has_accepted_protocol(url):
            raise PhantomCurlError('Unknown protocol for "{}"'.format(url))
        logger.info('fetching {}'.format(url))
        options_bin = ['--ignore-ssl-errors=true',
                       '--local-to-remote-url-access=true',
                       '--web-security=false']

#        options_bin += ['--disk-cache=true',
#                        '--max-disk-cache-size=10000'] # DEBUG
        if self._timeout_sec is None:
            timeout_js = None
            timeout_thread = None
        else:
            timeout_js = self._timeout_sec
            timeout_thread = timeout_js + self.TIMEOUT_JS_TO_JOIN_DELTA_SEC

        if self._cookie_jar:
            path = os.path.normpath(self._cookie_jar)
            options_bin.append(u'--cookies-file={:s}'.format(path))
        if self._proxy:
            options_bin.append(u'--proxy={:s}'.format(self._proxy))
        if self._debug:
            options_bin.append(u'--debug=true')
#        url_encoded =  urllib.quote(url, safe=u'/:')
        options_js = [_OPT_MAGIC_STRING, _MAGIC_STRING, _OPT_URL, url]
        if self._user_agent:
            options_js += [_OPT_USER_AGENT, self._user_agent]
        if capture_screen:
            options_js += [_OPT_CAPTURE_SCREEN, capture_screen]
        if self._inspect_iframes:
            options_js += [_OPT_INSPECT_IFRAMES]
        if timeout_js is not None:
            options_js += [_OPT_TIMEOUT_SEC, timeout_js]
        if self._delay is not None:
            options_js += [_OPT_DELAY_SEC, str(self._delay)]
        if not self._with_content:
            options_js += [_OPT_NO_CONTENT]
        if self._with_request_response:
            options_js += [_OPT_REQUEST_RESPONSE]
        if self._post_params is not None:
            options_js += [_OPT_POST_FULL, self._get_full_post_string()]

        options_js_str = [str(o) for o in options_js]
        cmds = [PHANTOMJS_BIN] + options_bin + [PHANTOMJS_JS] + options_js_str
        logger.debug('call {}'.format(cmds))
        out, err = command.call(cmds, timeout=timeout_thread)
        logger.debug('out: {:.1f}KB, err: {:.1f}KB'.format(
            len(out)/1000.0, len(err)/1000.0))
        if self._debug:
            logger.debug('stderr from phantomjs:')
            logger.debug(err)
        try:
            fixed_out = self._clean_output(out)
            output_json = json.loads(fixed_out)
        except ValueError:
            raise PhantomCurlError('Invalid output', out=out, err=err)
        return output_json

    def _get_full_post_string(self):
        return urllib.urlencode(self._post_params)

    def _clean_output(self, output):
        '''Cleaning output from garbage (from 0 to magic string)
           https://groups.google.com/forum/?fromgroups#!topic/phantomjs/LwRGJXpPsZA'''
        try:
            i = output.index(self._magic_string)
        except ValueError:
            fixed = output
            garbage = ''
        else:
            k = i + len(self._magic_string)
            fixed = output[k:]
            garbage = output[:i]
        if self._debug:
            logger.debug('garbage at output: {}B'.format(len(garbage)))
            if garbage:
                logger.debug(garbage)
        return fixed


def _split_post_tuples(post_data):
    '''post_data - collection of key=value strings. Returns list of (key,
    value) tuples. value can be '' '''
    return [split_post_data_item(item) for item in post_data]


def is_writeable(path):
    writeable = False
    try:
        with open(path, 'a'):
            writeable = True
    except IOError:
        pass
    return writeable


def _has_accepted_protocol(url):
    return any(url.startswith(proto) for proto in ['http://', 'https://'])


def split_post_data_item(post_item_string):
    '''key=(value)'''
    g = POST_DATA_ITEM_RE.match(post_item_string)
    if g is None:
        raise ValueError(repr(post_item_string))
    key, value = g.groups()
    return (key, value)


__all__ = [
    'PhantomCurl',
    'PhantomCurlError']

## notes
#
#    phantomjs [switchs] [options] [script] [argument [argument [...]]]
#   --cookies-file=<val>  
#   --ignore-ssl-errors=<val>  
#   --load-images=<val>       
#   --local-to-remote-url-access=true
#   --proxy=<val>                   

