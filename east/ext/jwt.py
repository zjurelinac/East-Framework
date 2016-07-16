"""
    east.ext.jwt
    ============
    Mock JWT authentication module
"""

import inspect

from east.app import Extension
from east.exceptions import HTTPUnauthorized


class EastJWT(Extension):

    def __init__(self, identity_verificator):
        self.identity_verificator = identity_verificator
        self.storage = None

    def install(self, app, ext_storage):
        self.storage = ext_storage
        self.storage.protected_routes = set()
        app.register_hook('endpoint_determined', self.endpoint_protection)

    def endpoint_protection(self, context):
        print(context.endpoint, self.storage.protected_routes)
        if (inspect.isfunction(context.endpoint) and context.endpoint in self.storage.protected_routes or
                isinstance(context.endpoint, tuple(self.storage.protected_routes))):
            print('testing')
            if not self.identity_verificator(context):
                raise JWTAuthorizationError('Authorization failed')

    def required(self, f):
        """Decorator for protecting routes"""
        print('protecting', f)
        self.storage.protected_routes.add(f)
        return f


class JWTAuthorizationError(HTTPUnauthorized):
    name = 'JWT Authorization Error'