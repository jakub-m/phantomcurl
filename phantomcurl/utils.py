import logging

__all__ = ['split_post_items', 'valid_data_pairs']


LOGGER_NAME = 'phantomcurl'
logger = logging.getLogger(LOGGER_NAME)


def split_post_items(post_items):
    '''['key=value', ...]. raises ValueError'''
    pairs = [tuple(pitem.split('=', 1)) for pitem in post_items]
    if any(len(kv) != 2 for kv in pairs):
        raise ValueError(post_items)
    return pairs


def valid_data_pairs(items):
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
