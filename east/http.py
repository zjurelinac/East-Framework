"""
    east.http
    =========
    HTTP request and response classes and various related functions

    :copyright: (c) 2016 by Zvonimir Jurelinac
    :license: MIT
"""

import json
import urllib.parse

from east.structures import Headers, WSGIHeaders
from east.exceptions import *
from east.functions import identity


class Request:
    """HTTP request representation"""

    def __init__(self, url, method, environ, body=None, headers=None, args={}):
        self.url = url
        self.method = method
        self.environ = environ
        self.headers = headers
        self.args = args
        self.body = {}

    @classmethod
    def parse_request(cls, environ):
        """"""
        request_url = '/' + environ['PATH_INFO'].lstrip('/')
        request_method = environ['REQUEST_METHOD']
        http_headers = WSGIHeaders(environ)
        request_args = parse_urlencoded_args(environ['QUERY_STRING'])
        body = parse_request_body(environ['wsgi.input'], http_headers) if http_headers.get('Content-Length', "0") != "0" else {}
        return cls(request_url, request_method, environ, body=body, headers=http_headers, args=request_args)


class Response:
    """HTTP response representation"""

    def __init__(self, body, status=200, headers=None, content_type='text/plain', **kw_headers):
        self.body = body
        self.status = status
        self.headers = Headers()
        self.headers['Content-Type'] = self.content_type = content_type
        self.content_length = len(body)
        self.headers['Content-Length'] = str(self.content_length)

    @property
    def status_message(self):
        return '%d %s' % (self.status, HTTP_MESSAGES[self.status])


def parse_urlencoded_args(query_string):
    """Generate a key-value dict representing parameters from urlencoded string"""
    return {k: (v[0] if len(v) == 1 else v) for k, v in urllib.parse.parse_qs(query_string, keep_blank_values=True).items()}


def parse_request_body(input_stream, http_headers):
    """"""
    content_type = http_headers['Content-Type']
    content_length = http_headers['Content-Length']

    if content_length > MAX_REQUEST_BODY_SIZE:
        raise RequestBodyTooLarge

    if content_type == 'application/json':
        parser = json.loads
    elif content_type == 'application/x-www-form-urlencoded':
        parser = parse_urlencoded_args
    elif content_type == 'multipart/form-data':
        raise NotImplementedError('Parsing multipart/form-data is not (yet) supported')
    elif content_type == 'text/plain':
        parser = identity
    else:
        raise UnknownRequestBodyType

    return parser(input_stream.read(content_length).decode())

MAX_REQUEST_BODY_SIZE = 100 * 1024

HTTP_MESSAGES = {
    100: 'Continue',
    101: 'Switching Protocols',

    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',

    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',

    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Payload Too Large',
    414: 'URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Range Not Satisfiable',
    417: 'Expectation Failed',
    418: 'I\'m a teapot',
    421: 'Misdirected Request',
    426: 'Upgrade Required',
    428: 'Precondition Required',
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',

    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    506: 'Variant Also Negotiates'
}
