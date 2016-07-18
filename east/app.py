"""
    east.app
    ========

"""

import logging
import sys
# import traceback

from abc import ABCMeta, abstractmethod
from collections import defaultdict

from east.http import Request
from east.routing import Router, Resource, dispatch_to_endpoint
from east.exceptions import *


class East:
    """Application object

    Provides WSGI interface, routing, configurations, event management and
    error handling.
    """

    def __init__(self, name):
        self.name = name

        self._router = Router()
        self._config = self.make_config()
        self._logger = self.make_logger()
        self._ext = {}
        self._hooks = defaultdict(list)
        self._exception_handlers = {}

        self.logger.info('App `%s` initialized' % self.name)
        self.logger.warning('Config not properly implemented yet!')

    # Routing, customization and extension points

    def register_route(self, f, url_rule, methods):
        """Register a view function/method for a given URL rule"""
        self._router.add_route(f, url_rule, methods)

    def register_hook(self, event, f):
        """Register a function which will be executed upon firing of the event"""
        self._hooks[event].append(f)

    def register_errorhandler(self, exception, f):
        """Register an error handler for a specific exception"""
        self._exception_handlers[exception] = f

    def register_extension(self, extension, name=None):
        """"""
        if name is None:
            name = extension.__class__.__qualname__
        self._ext[name] = DataStorage()

        extension.install(self, self._ext[name])

    # Decorators

    def route(self, url_rule, methods=['GET']):
        """Decorator for registering view functions for an URL"""
        def decorator(f):
            self.register_route(f, url_rule, methods)
            return f
        return decorator

    def resource(self, url_rule):
        """Decorator for registering resources for an URL"""
        def decorator(cls):
            self.register_route(cls, url_rule, None)
            return cls
        return decorator

    def event_hook(self, event):
        """Decorator for registering hooks for specific events"""
        def decorator(f):
            self.register_hook(event, f)
            return f
        return decorator

    def error_handler(self, exception):
        """Decorator for registering error (exception) handlers"""
        def decorator(f):
            self.register_errorhandler(exception, f)
            return f
        return decorator

    # Configuring, testing, debugging and logging

    def make_config(self):
        config = {'DEBUG': True}
        return config

    def make_logger(self):
        level = logging.DEBUG if self.config.get('DEBUG') else logging.ERROR

        logger = logging.getLogger(self.name)
        logger.setLevel(level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s | %(levelname)-9s| %(name)-20s :: %(message)s', '%d/%m/%Y %H:%M:%S')

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    @property
    def config(self):
        return self._config

    @property
    def logger(self):
        return self._logger

    def run(self, host, port=8000):
        try:
            from gevent.pywsgi import WSGIServer
        except ImportError:
            self.logger.log('Could not find gevent package, aborting')
            sys.exit(1)

        server = WSGIServer((host, port), self, log=self.logger)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Shutting down... Bye bye!')
            server.stop()

    # Execution methods

    def dispatch_to_handler(self, exception):
        """Dispatch caught exception to it's registered handler"""
        for exc_class, exc_handler in self._exception_handlers.items():
            if isinstance(exception, exc_class):
                return exc_handler(exception)
        return None

    def trigger_event(self, event, context):
        """Activate all hooks listening to the event"""
        for hook in self._hooks[event]:
            hook(context)

    def application(self, environ, start_response):
        """The WSGI application"""
        try:
            context = Context(self, environ)
            response, status, exception = context.execute()
            if status == Context.ERROR:
                response = self.dispatch_to_handler(exception) or exception.as_response()
        except Exception as e:
            self.logger.exception('Caught exception during request serving (with traceback):')
            response = HTTPBaseException(str(e), name=e.__class__.__name__).as_response()
        finally:
            self.logger.info('%s %s :: %s' % (context.request.method, context.request.url, response.status_message))
            start_response(response.status_message, response.headers.as_list())
            return [response.body]

    def __call__(self, environ, start_response):
        """Shortcut for method self.application"""
        return self.application(environ, start_response)


class Context:
    """Request-serving context, wraps processing of a single request"""

    CREATED = 0
    FINISHED = 1
    ERROR = -1

    def __init__(self, app, environ):
        self.environ = environ
        self.request = None
        self.endpoint = None
        self.response = None
        self.exception = None

        self.error_stream = environ['wsgi.errors']

        self.config = app.config
        self.data = DataStorage()
        self.logger = app.logger

        self.trigger_event = app.trigger_event
        self.match_route = app._router.match

        self.status = Context.CREATED

    def execute(self):
        """Execute request processing and content generation, all inside
        the current context"""
        try:
            self.trigger_event('context_created', self)

            self.request = Request.parse_request(self.environ)
            self.trigger_event('request_received', self)

            self.determine_endpoint()
            self.trigger_event('endpoint_determined', self)

            self.dispatch_request()
            self.trigger_event('response_created', self)

            self.status = Context.FINISHED
        except Exception as e:
            if self.config.get('DEBUG'):
                self.logger.exception('Request processing ended with exception:')
            self.status = Context.ERROR
            self.exception = HTTPBaseException(str(e), name=e.__class__.__name__).with_traceback(sys.exc_info()[2])
        finally:
            return self.response, self.status, self.exception

    def determine_endpoint(self):
        """Determine which resource/view is located at the given URL, and extract URL parameters"""
        self.endpoint, self.request.url_parameters = self.match_route(self.request.url, self.request.method)

    def dispatch_request(self):
        """Dispatch request to the endpoint resource and obtain the response"""
        self.response = (self.endpoint()(self) if issubclass(self.endpoint, Resource)
                         else dispatch_to_endpoint(self.endpoint, self))

    def retrieve_param(self, param_name):
        """Return parameter value from the request context, or None if it's not there"""
        locations = [self.request.url_parameters, self.request.args]

        if self.request.method in ('POST', 'PUT', 'PATCH'):
            locations.append(self.request.body)

        for location in locations:
            if param_name in location:
                return location[param_name]


class Extension:
    """Abstract base class for all East extension modules

    Each extension must support the `install` method which is called upon extension
    registration with the application object
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def install(self, app, ext_storage):
        pass


class DataStorage:
    """Custom object meant to serve as data storage, fully customizable"""
    pass
