(function(){ // BEGIN STRICT
"use strict";

/* Version of JS script (only JS, not the whole package) */
var VERSION                 = 'r20';

/* Accepted command line arguments. Other arguments might go to directly to
 * PhantomJS */

/* URL to be fetched */
var OPT_URL                 = '--url';

/* Set User-Agent */
var OPT_USER_AGENT          = '--user-agent';

/* String that is printed immediately before the real output data. Separates
 * garbage at output from the real output. Any (random) string will do. */
var OPT_MAGIC_STRING        = '--magic-string';

/* Make screenshot */
var OPT_CAPTURE_SCREEN      = '--capture-screen';

/* Recursively inspect iframes */
var OPT_INSPECT_IFRAMES     = '--inspect-iframes';

/* Kill after X seconds. Accepts fractions of second. */
var OPT_TIMEOUT_SEC         = '--timeout-sec';

/* Wait additional X seconds */
var OPT_DELAY_SEC           = '--delay-sec'

/* do not print content */
var OPT_NO_CONTENT          = '--no-content'

/* capture requests and responses */
var OPT_REQUEST_RESPONSE    = '--request-response'

/* --post key value --post key2 value */
var OPT_POST_FULL           = '--post-full'

/* optional custom headers, passed as JSON-ified dictionary */
var OPT_CUSTOM_HEADERS_JSON = '--custom-headers-json'

/*************************************************************************/

var system = require( 'system' );


var die = function(message) {
    console.error("error: " + message);
    phantom.exit(-1);
};


var parse_arguments = function() {
    var args = system.args.slice(1);
    var opts = {inspect_iframes: false,
                with_content: true,
                with_request_responses: false,
                method: 'GET',
                post: {} };

    while(args.length) {
        var x = args.shift();
        switch (x) {
            case OPT_URL:
                opts.url = args.shift();
                break;
            case OPT_USER_AGENT:
                opts.user_agent = args.shift();
                break;
            case OPT_MAGIC_STRING:
                opts.magic_string = args.shift();
                break;
            case OPT_CAPTURE_SCREEN:
                opts.capture_screen = args.shift();
                break;
            case OPT_INSPECT_IFRAMES:
                opts.inspect_iframes = true;
                break;
            case OPT_TIMEOUT_SEC:
                opts.timeout_sec = parseFloat(args.shift());
                break;
            case OPT_DELAY_SEC:
                opts.delay_sec = parseFloat(args.shift());
                break;
            case OPT_NO_CONTENT:
                opts.with_content = false;
                break;
            case OPT_REQUEST_RESPONSE:
                opts.with_request_responses = true;
                break;
            case OPT_POST_FULL:
                opts.method = 'POST';
                opts.post_full_str = args.shift();
                break;
            case OPT_CUSTOM_HEADERS_JSON:
                opts.custom_headers = JSON.parse(args.shift());
                break;
            default:
                die('unknown option: ' + x);
        }
    }
    return opts;
};


var get_timestamp = function() {
    return (new Date().getTime()) / 1000.0;
};


/* recursively inspect iframes in the page */
var iframes_deep_inspection = function(page)
{
    var frames_found = page.evaluate(function() {
        return (function() {
            var frames_root = [];
            var find_frames_rec = function(doc, container) {
                var frames = doc.getElementsByTagName('iframe');
                for (var i_frame = 0; i_frame < frames.length; i_frame++) {
                    var frame = frames[i_frame];
                    var inner_doc = frame.contentDocument;
                    var content = undefined;
                    var inner_frames = [];
                    if (undefined === inner_doc) {
                        content = null;
                    } else {
                        try {
                            content = inner_doc.documentElement.innerHTML;
                            find_frames_rec(inner_doc, inner_frames);
                        } catch (e) {
        //                    if (e instanceof TypeError) {
        //                     /* thrown when protocols do not match */
        //                    } else {
        //                       throw e;
        //                    }
                        }
                    }
                    var meta = {content: content,
                                frames: inner_frames};
                    var frame_attrs = ['src', 'id', 'name', 'height', 'width'];
                    for (var i_attr = 0; i_attr < frame_attrs.length;
                         i_attr++) {
                        var attr_key = frame_attrs[i_attr];
                        var attr_value = frame[attr_key];
                        if (undefined !== attr_value && '' !== attr_value) {
                            meta[attr_key] = attr_value;
                        }
                    }
                    container.push(meta);
                };
            }; // end find_frames_rec
            find_frames_rec(document, frames_root);
            return frames_root;
        })();

    });
    return frames_found;
}

/*********************************  main  ***********************************/

var g_opts = parse_arguments();
var all_requests = undefined;
var all_responses = undefined;

var page = require('webpage').create();

if (g_opts.url === undefined) {
    console.error("--url missing");
    phantom.exit(-1);
}

if (g_opts.user_agent !== undefined) {
    page.settings.userAgent = g_opts.user_agent;
}

if (g_opts.custom_headers !== undefined) {
    page.customHeaders = g_opts.custom_headers;
}

if (g_opts.with_request_responses == true) {
    all_requests = [];
    all_responses = [];
    /* Record requests and responses */
    page.onResourceRequested = function(requestData, networkRequest) {
        all_requests.push(requestData);
    };
    
    page.onResourceReceived = function(responseData) {
        all_responses.push(responseData);
    };
}

var timestamp_start = get_timestamp();

var g_output_data = {};

var record_error = function(error_message)
{
    if (undefined === g_output_data.errors) {
        g_output_data.errors = [];
    }
    g_output_data.errors.push(error_message);
}


/* One true exit point. Print the results as JSON and exit phantomjs. */
var finish = function() {
    if (g_opts.magic_string) {
        console.log(g_opts.magic_string);
    }
    var pretty = JSON.stringify(g_output_data, null, " ");
    console.log(pretty);
    phantom.exit();
};

/* Record errors on page */
page.onError = function(msg, trace) {
    var error_msg = 'PHANTOMJS page.onError: ' + msg;
    record_error(error_msg);
};

phantom.onError = function(msg, trace) {
    var error_msg = 'PHANTOMJS phantom.onError: ' + msg;
    console.error(error_msg);
    record_error(error_msg);
    finish();
};

if (undefined !== g_opts.timeout_sec) {
    setTimeout(function(){
        /* If page hangs on page.open, then this timeout will kill it */
        record_error('Timeout expired');
        finish();
    }, g_opts.timeout_sec * 1000);
}

page.open(g_opts.url, g_opts.method, g_opts.post_full_str,
          function (page_status) {
    var process_page = function() {
        if (g_opts.capture_screen) {
            page.render(g_opts.capture_screen);
        }

        var frames = undefined;
        if (g_opts.inspect_iframes) {
            frames = iframes_deep_inspection(page);
        }

        var content_out = (g_opts.with_content ? page.content : undefined);
        var timestamps =  {start: timestamp_start, end: get_timestamp()};

        var output_data = {
            url:            page.url,
            original_url:   g_opts.url,
            requests:       all_requests,
            responses:      all_responses,
            content:        content_out,
            timestamps:     timestamps,
            frames:         frames,
            version:        VERSION,
            command_line:   system.args
        };

        g_output_data = output_data;
        finish();
    };

    var delay_sec = g_opts.delay_sec;
    if (undefined === delay_sec) {
        process_page();
    } else {
        console.error('waiting ' + delay_sec + ' seconds');
        setTimeout(function() { process_page() }, (delay_sec * 1000.0));
    }
});

})(); // END STRICT


/* --- NOTES ---

Use this snippet to set custom headers for proxy:

    var HEADER_PROXY_DUMP = 'X-Proxy-Dump-File'
    var headers = {}
    headers[HEADER_PROXY_DUMP] =  g_opts.x_proxy_dump_prefix
    page.customHeaders = headers


phantom.onError = function(msg, trace) {
    console.log('debug3');
    var msgStack = ['PHANTOM ERROR: ' + msg];
    if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function(t) {
            msgStack.push(' -> ' + (t.file || t.sourceURL) + ': ' + t.line + (t.function ? ' (in function ' + t.function + ')' : ''));
        });
    }
    console.error(msgStack.join('\n'));
    phantom.exit(1);
};

*/


