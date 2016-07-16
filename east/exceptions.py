"""
    east.exceptions
    ===============
    Definitions of HTTP and other application exceptions, used inside
    framework implementation as well as in client code.

    :copyright: (c) 2016 by Zvonimir Jurelinac
    :license: MIT
"""


class HTTPBaseException(Exception):
    """Base exception, can be represented as an HTTP response"""
    status_code = 500
    name = 'HTTP Base Exception'

    def __init__(self, description='', name=None):
        self.description = description
        if name is not None:
            self.name = name

    def __str__(self):
        return '<%s>: %s' % (self.name, self.description)

    def as_response(self):
        from east.http import Response
        from east.functions import make_json
        return Response(make_json({'code': self.status_code, 'name': self.name,
                                   'description': self.description}), self.status_code)


class HTTPBadRequest(HTTPBaseException):
    status_code = 400
    name = 'Bad Request'


class HTTPUnauthorized(HTTPBaseException):
    status_code = 401
    name = 'Unauthorized'


class HTTPPaymentRequired(HTTPBaseException):
    status_code = 402
    name = 'Payment Required'


class HTTPForbidden(HTTPBaseException):
    status_code = 403
    name = 'Forbidden'


class HTTPNotFound(HTTPBaseException):
    status_code = 404
    name = 'Not Found'


class HTTPMethodNotAllowed(HTTPBaseException):
    status_code = 405
    name = 'Method Not Allowed'


class HTTPNotAcceptable(HTTPBaseException):
    status_code = 406
    name = 'Not Acceptable'


class HTTPProxyAuthenticationRequired(HTTPBaseException):
    status_code = 407
    name = 'Proxy Authentication Required'


class HTTPRequestTimeout(HTTPBaseException):
    status_code = 408
    name = 'Request Timeout'


class HTTPConflict(HTTPBaseException):
    status_code = 409
    name = 'Conflict'


class HTTPGone(HTTPBaseException):
    status_code = 410
    name = 'Gone'


class HTTPLengthRequired(HTTPBaseException):
    status_code = 411
    name = 'Length Required'


class HTTPPreconditionFailed(HTTPBaseException):
    status_code = 412
    name = 'Precondition Failed'


class HTTPPayloadTooLarge(HTTPBaseException):
    status_code = 413
    name = 'Payload Too Large'


class HTTPURITooLong(HTTPBaseException):
    status_code = 414
    name = 'URI Too Long'


class HTTPUnsupportedMediaType(HTTPBaseException):
    status_code = 415
    name = 'Unsupported Media Type'


class HTTPRangeNotSatisfiable(HTTPBaseException):
    status_code = 416
    name = 'Range Not Satisfiable'


class HTTPExpectationFailed(HTTPBaseException):
    status_code = 417
    name = 'Expectation Failed'


class HTTPTooManyRequests(HTTPBaseException):
    status_code = 429
    name = 'Too Many Requests'


class HTTPRequestHeaderFieldsTooLarge(HTTPBaseException):
    status_code = 412
    name = 'Request Header Fields Too Large'


class HTTPInternalServerError(HTTPBaseException):
    status_code = 500
    name = 'Internal Server Error'


class HTTPNotImplemented(HTTPBaseException):
    status_code = 501
    name = 'Not Implemented'


# Application-specific errors

class RequestParseError(HTTPBadRequest):
    name = 'Request Parse Error'


class UnexpectedResponseType(HTTPInternalServerError, TypeError):
    name = 'Unexpected Response Type'


class ContextExecutionError(HTTPInternalServerError, RuntimeError):
    name = 'Context Execution Error'


class UnknownRequestBodyType(HTTPBadRequest, TypeError):
    name = 'Unknown Request Body Type'


class RequestBodyTooLarge(HTTPBadRequest, ValueError):
    name = 'Request Body Too Large'


# Utility exceptions

class ImmutableValueChange(HTTPInternalServerError, ValueError):
    name = 'Immutable Value Change'
