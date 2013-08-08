from nose.tools import *

from phantomcurl.utils import split_post_items


def test_post_data_good():
    expected_given = [
        ([('foo', 'bar')], ['foo=bar']),
        ([('foo', '')], ['foo=']),
        ([('foo', '=')], ['foo==']),
        ([('', '')], ['=']),
        ([('', '=')], ['==']),
        ([('', 'bar')], ['=bar'])
    ]

    for expected, given in expected_given:
        yield check_post_data_good, expected, given


def check_post_data_good(expected_dict, post_items):
    post_dict = split_post_items(post_items)
    assert_equals(expected_dict, post_dict)


def test_post_data_bad():
    bad_input = ['foo', '']
    for input_item in bad_input:
        yield check_post_data_bad, input_item


def check_post_data_bad(post_item):
    assert_raises(ValueError, split_post_items, [post_item])


#def test_dict_to_post_string():
#    assert_in(
#        dict_to_post_string({'foo', 'bar'}),
#        ['foo=bar'])
#    assert_in(
#        dict_to_post_string({'foo': '', 'ham': 'spam '}),
#        ['foo=&ham=spam+', 'ham=spam+&foo=']
#    )
