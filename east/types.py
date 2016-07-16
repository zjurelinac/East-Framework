"""
    east.types
    ==========
    Endpoint output types and response generation

    :copyright: (c) 2016 by Zvonimir Jurelinac
    :license: MIT
"""

from east.exceptions import *
from east.http import Response


class ResponseType:
    """Response type base class, contains format static method"""

    def format(self, obj, status=200):
        raise NotImplementedError


class JSON(ResponseType):
    """JSON response formatter

    Expects the return object to be either directly serializable as JSON,
    or to implement a to_jsondict method.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def format(self, obj, status=200):
        from east.functions import make_json
        try:
            encoded = make_json(obj)
        except ValueError:
            if hasattr(obj, 'to_jsondict'):
                encoded = make_json(obj.to_jsondict(**self.kwargs))
            else:
                raise UnexpectedResponseType('%s cannot be converted to JSON format.' % obj)
        finally:
            return Response(encoded, status, content_type='application/json')


class Str(ResponseType):
    """Plain text response formatter, converts the returned object to string"""

    def format(self, obj, status=200):
        return Response(str(obj).encode('utf8'), status)


class Nothing(ResponseType):
    """No response formatter, generates empty response body"""

    def format(self, obj, status=204):
        if obj is not None:
            raise TypeError('Incorrect response format, expected None')
        return Response('', status, content_type=None)
