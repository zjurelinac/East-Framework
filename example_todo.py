from east import East, JSON, Nothing, Resource, Response
from east.ext.jwt import *


def auth(context):
    return True

app = East()

jwt = EastJWT(auth)
app.register_extension(jwt)

todos = {}


class MyException(Exception):
    pass


@app.resource('/misc')
@jwt.required
class Misc(Resource):

    def get(self, id: int = 7) -> JSON:
        return {'message': {'text': 'hello', 'id': id}}


@app.resource('/todos')
class Todos(Resource):

    def get(self) -> JSON:
        return todos


@app.resource('/todos/<int:todo_id>')
class Todo(Resource):

    def get(self, todo_id: int) -> JSON:
        return todos[todo_id]

    def put(self, todo_id: int, task: str) -> JSON(full=True):
        todos[todo_id] = task
        return task

    def delete(self, todo_id: int) -> Nothing:
        del todos[todo_id]
        return None, 204


@app.error_handler(MyException)
def handle_my_exception(exc):
    print(exc)
    return Response('Error happened', 404)
