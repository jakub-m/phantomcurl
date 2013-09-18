from nose.tools import assert_equals, assert_raises

import phantomcurl.utils


def test_split_headers():
    test_vector = [
        ([], []),
        ([['foo']], [('foo', '')]),
        ([['foo', 'bar']], [('foo', 'bar')]),
        ([['foo', 'bar'], ['baz']], [('foo', 'bar'), ('baz', '')])]
    for input_, expected in test_vector:
        yield check_split_headers, input_, expected


def check_split_headers(input_, expected):
    output_ = phantomcurl.utils.valid_data_pairs(input_)
    assert_equals(expected, output_)


def test_raise_on_bad_input():
    bad_input = [['foo', 'bar', 'baz']]
    assert_raises(ValueError, phantomcurl.utils.valid_data_pairs, bad_input)
