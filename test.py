import functools
import inspect
import json

from flask import Flask, request, Response


app = Flask(__name__)


class JSON(type):
    def format(obj):
        try:
            return json.dumps(obj)
        except TypeError:
            return 'Wont do'


def _obtain_from_request(param_name, default=None):
    """Obtain a `param_name` argument from request parameters"""
    if request.method in ('GET', 'DELETE'):
        if param_name in request.args:
            return request.args[param_name]
        elif param_name in request.cookies:
            return request.cookies[param_name]
        elif param_name in request.headers:
            return request.headers[param_name]
        elif default is not None:
            return default
        else:
            raise Exception('Parameter `%s` is missing from the request.' % param_name)
    elif request.method in ('POST', 'PUT'):
        if param_name in request.form:
            return request.form[param_name]
        elif(request.get_json(silent=True) is not None and
                param_name in request.get_json(silent=True)):
            return request.get_json(silent=True).get(param_name)
        elif param_name in request.files:
            return request.files[param_name]
        elif param_name in request.cookies:
            return request.cookies[param_name]
        elif param_name in request.headers:
            return request.headers[param_name]
        elif default is not None:
            return default
        else:
            raise Exception('Parameter `%s` is missing from the request.' % param_name)
    else:
        raise Exception('Unsupported method for a given route.')


def easter(route, defaults={}):
    def decorator(f):
        @functools.wraps(f)
        @app.route(route, defaults=defaults)
        def decorated_function(*args, **kwargs):
            params = {}
            # params.update(kwargs)
            for param in inspect.signature(f).parameters.values():
                raw_value = _obtain_from_request(param.name, default=param.default
                                                 if param.default is not inspect._empty else None)
                params[param.name] = param.annotation(raw_value)
                # TODO: Add parameter validation
            output_type = f.__annotations__['return']
            return Response(output_type.format(f(**params)), mimetype='application/json')
        return decorated_function
    return decorator


@easter('/hello/<int:id>/<value>')
def index(x: int, y: str="abeceda") -> JSON:
    return {'data': [x, y]}


if __name__ == '__main__':
    app.run(debug=True, port=8000)
