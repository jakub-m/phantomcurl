import logging

LOGGER_NAME = 'phantomcurl'
logger = logging.getLogger(LOGGER_NAME)


def split_post_items(post_items):
    '''['key=value', ...]. raises ValueError'''
    pairs = [tuple(pitem.split('=', 1)) for pitem in post_items]
    if any(len(kv) != 2 for kv in pairs):
        raise ValueError(post_items)
    return pairs
