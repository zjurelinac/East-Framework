from east import East, JSON, Nothing, Resource, Response
from east.ext.jwt import *


app = East(__name__)

jwt = EastJWT(lambda x: True)
app.register_extension(jwt)

todos = {}


class MyException(Exception):
    pass


@app.route('/misc', methods=['GET'])
@jwt.required
def get_misc(id: int = 7) -> JSON:
    return {'message': {'text': 'hello', 'id': id}}


@app.resource('/todos')
class Todos(Resource):

    def get(self) -> JSON:
        return todos


@app.resource('/todos/<int:todo_id>')
class Todo(Resource):

    def get(self, todo_id: int) -> JSON:
        raise MyException('hello world')
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


if __name__ == '__main__':
    app.run('localhost')
