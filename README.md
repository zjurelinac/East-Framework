# EAST (pf)
_Easy REST Python Framework_

A simple, easy-to-use Python framework for building RESTful APIs. It's intention
is to make developing APIs in Python as intuitive as possible, providing highly
expressive and clean syntax with as little boilerplate code as possible.

East was started as a personal project inspired by experiences of developing applications 
in Flask, with the idea of combining all the best features of Flask with built-in
flexibility of Python and a few ideas of functional programming.

### Features of EAST include:
  - **Resource-** or **view-based** routing with **URL parameters**
  - Route parameter and return type definitions using **Python type hints**
  - Custom parameter types providing **input validation**
  - Builtin support for **JSON** (and soon XML) **based APIs**
  - **Automatic generation of API docs** from source code and pydoc
  - API exception handling - simplifies development and operation
  - **Extremely easy to extend** the workings of EAST with events and hooks
  - Comes with **extensions** for:
    - **Database management** (using Peewee)
    - **API authentication** (Basic auth, JWT)
    - **Caching** (not yet)

## A few examples

```python
# The simplest of examples: the proverbial TODO app

app = East(__name__)
todos = {}

@app.resource('/api/todos/<int:id>')
class TodoResource(Resource):
    """A simple todo-list item"""
    
    def get(self, id: int) -> JSON:
        return todos[id]

    def put(self, id: int, task: str) -> JSON:
        todos[id] = task
        return todos[id]

    def delete(self, id: int) -> Nothing:
        del todos[id]
```

## Future ideas
- HTML templating via output type (extension)
- Input stream wrapping, if neccessary - YES, will use for testing
- Allow app functional testing - use mock WSGI server (create WSGI envirnoment, return response to the tester)

## TODO / Status
- [x] Implement logging
- [x] Implement app.run()
- [ ] JWT & basic auth extensions
- [ ] Database extensions
- [ ] Support setting response header inside view
- [ ] Add cookie support - setting and getting
- [ ] Introduce 405 MethodNotAllowed errors
- [ ] Support OPTIONS HTTP request
- [ ] Allow multipart/formdata request body
- [ ] Allow file upload via arbitrary request body content-type
- [ ] Add API Regions
- [ ] AUTOMATIC DOCS GENERATION

