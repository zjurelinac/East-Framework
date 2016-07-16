"""
    east.structures
    ===============
    Defines data structures used in Request/Response parsing and generation

    :copyright: (c) 2016 by Zvonimir Jurelinac
    :license: MIT
"""


from collections import defaultdict
from collections.abc import Mapping, MutableMapping

from east.exceptions import *
from east.functions import make_list


# Generic data structures

class ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise ImmutableValueChange('Cannot modify ImmutableDict element value.')

    def __delitem__(self, key):
        raise ImmutableValueChange('Cannot delete ImmutableDict element.')


class WSGIHeaders(Mapping, ImmutableDict):
    """Case-insensitive WSGI HTTP headers dictionary. Read-only."""

    def __init__(self, environ):
        self.dict = {normalize_http_header(k[5:]): self.parse_header_value(v)
                     for k, v in environ.items() if k.startswith('HTTP_')}
        self.content_type = environ.get('CONTENT_TYPE', None)
        self.content_length = int(environ.get('CONTENT_LENGTH', 0))

    def __getitem__(self, key):
        return self.dict[normalize_http_header(key)]

    def __iter__(self):
        return iter(self.dict)

    def __len__(self):
        return len(self.dict)

    def __contains__(self, key):
        return normalize_http_header(key) in self.dict

    def parse_header_value(self, header):
        header_values = []
        for value_item in header.split(','):
            value_item = value_item.strip()
            if '(' not in value_item:
                value, *params = value_item.split(',')
                value_item = HeaderValue(value)
                value_item.params = {k.strip(): v.strip() for (k, v) in [x.split('=', 1) for x in params]}
            header_values.append(value_item)
        return header_values[0] if len(header_values) == 1 else header_values or None


class Headers(MutableMapping):
    """Case-insensitive HTTP headers dictionary."""

    def __init__(self, headers=None):
        self.store = defaultdict(list)

        if headers is not None:
            self.store.update(headers)

    def __getitem__(self, key):
        return self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __setitem__(self, key, value):
        self.store[key] = make_list(value)

    def __delitem__(self, key):
        del self.store[key]

    def as_list(self):
        """Return self represented as a list of key-value tuples"""
        return [(normalize_http_header(k), ','.join(v)) for k, v in self.store.items()]


class HeaderValue(str):
    pass


def normalize_http_header(header_name):
    UPPERCASE = ('http', 'dnt', 'xml')
    return '-'.join([x.upper() if x in UPPERCASE else x.capitalize() for x in header_name.split('-')])
