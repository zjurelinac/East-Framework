"""
    east.functions
    ==============
    A set of functional programming utility functions for internal use

    :copyright: (c) 2016 by Zvonimir Jurelinac
    :license: MIT
"""

import json

from collections.abc import Sequence


def identity(x):
    return x


# Data conversion

def make_json(obj):
    return json.dumps(obj, indent=4, separators=(', ', ': ')).encode('utf8')


def make_list(obj):
    return list(obj) if isinstance(obj, Sequence) and not isinstance(obj, str) else [obj]
