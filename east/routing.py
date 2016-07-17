"""
    east.routing
    ============
    URL routing implementation

    :copyright: (c) 2016 by Zvonimir Jurelinac
    :license: MIT
"""

import inspect
import re

from east.exceptions import *


class Resource:
    """REST API Resource representation"""

    def __call__(self, context):
        """Dispatches a request (wrapped in context) to the proper resource method"""
        method = context.request.method.lower()
        if not hasattr(self, method):
            raise HTTPMethodNotAllowed('`%s` does not support %s method' % (self.__class__.__name__, method.upper()))

        return dispatch_to_endpoint(getattr(self, method), context)

    def list_methods(self):
        pass


class Route:
    """Single route representation"""
    _separator_pattern = re.compile('(<|:|>)')
    _type_regexes = {'int': '[0-9]+', 'string': '[^\]+', 'path': '.+'}
    _type_parsers = {'int': int, 'string': str, 'path': str}

    def __init__(self, endpoint, url_rule, methods=['GET']):
        self.endpoint = endpoint
        self.url_rule = url_rule
        self.methods = [x.upper() for x in methods] if methods is not None else None
        self.raw_regex, self.adapted_regex, self.url_parameters = Route.make_regex(url_rule)
        self.compiled_regex = re.compile(self.raw_regex)

    @staticmethod
    def make_regex(url_rule):
        """"""
        rule_tokens = Route._separator_pattern.split(url_rule)
        parsed_tokens, adapted_tokens = [], []
        url_parameters = {}
        var_name_next, var_type_next = False, False
        last_var_type = None
        for token in rule_tokens:
            if token == '<':
                var_type_next = True
            elif token == '>':
                pass
            elif token == ':':
                var_name_next = True
            elif var_type_next:
                last_var_type = token
                var_type_next = False
            elif var_name_next:
                parsed_tokens.append('(?P<%s>%s)' % (token, Route._type_regexes[last_var_type]))
                adapted_tokens.append('(?:%s)' % Route._type_regexes[last_var_type])
                url_parameters[token] = last_var_type
                var_name_next = False
            else:
                parsed_tokens.append(token)
                adapted_tokens.append(token)
        return ''.join(parsed_tokens), ''.join(adapted_tokens), url_parameters

    def encode_methods(self):
        """"""
        return r'\[(?:%s)\]' % '|'.join(self.methods) if self.methods is not None else r'\[.+\]'

    def parse_url_parameters(self, url):
        """"""
        return {k: self._type_parsers[self.url_parameters[k]](v) for k, v
                in self.compiled_regex.match(url).groupdict().items()}


class Region:
    """API route/resource group, with a common URL prefix"""
    pass


class Router:
    """Routing provider"""

    def __init__(self):
        self.routes = []
        self._matcher = None

    def add_route(self, endpoint, url_rule, methods):
        """"""
        route = Route(endpoint, url_rule, methods)
        self.routes.append(route)

    def initialize(self):
        """"""
        combined_regex = '|'.join([r'(%s%s)' % (route.encode_methods(), route.adapted_regex) for route in self.routes])
        self._matcher = re.compile(combined_regex)

    def match(self, url, method):
        """"""
        if self._matcher is None:
            self.initialize()
        match = self._matcher.fullmatch('[%s]%s' % (method.upper(), url))

        if match is not None:
            match_route = self.routes[[i for i, u in enumerate(match.groups()) if u is not None][0]]
            return match_route.endpoint, match_route.parse_url_parameters(url)
        else:
            raise HTTPNotFound('Cannot resolve route')


def dispatch_to_endpoint(endpoint, context):
    """Handles dispatching of a request to the endpoint

    This includes parsing and validating request arguments, invoking endpoint
    function/method and formatting the output result.
    """
    params = {}
    for param in inspect.signature(endpoint).parameters.values():
        default = param.default if param.default is not inspect._empty else None
        raw_value = context.retrieve_param(param.name) or default
        if raw_value is None:
            raise HTTPBadRequest('Required parameter `%s` is missing from the request' % param)
        params[param.name] = param.annotation(raw_value)

    output_type = endpoint.__annotations__['return']
    if inspect.isclass(output_type):
        output_type = output_type()

    output = endpoint(**params)
    status = 200
    if isinstance(output, tuple):
        output, status = output
    return output_type.format(output, status)
