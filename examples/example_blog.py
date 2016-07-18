from east import East, JSON


app = East()


class Topic:
    pass


class Post:
    pass


class Comment:
    pass


@app.resource('/topics')
class Topics:
    """Collection of topics, supports list(GET) and add(POST)"""

    def get(self) -> JSON:
        pass


@app.resource('/topics/<int:topic_id>')
class Topic:
    """Single topic, supports retrieve (GET), edit (PUT, add PATCH later)
    and remove(DELETE)"""

    def get(self, topic_id: int) -> str:
        return 'Hello, man'

    def put(self, topic_id: int, name: str, description: str) -> JSON:
        return {'topic_id': topic_id, 'name': name, 'description': description}

    def delete(self, topic_id: int) -> None:
        pass


@app.resource('/topics/<int:topic_id>/posts')
class Posts:
    """"""


@app.resource('/topics/<int:topic_id>/posts/<int:post_id>')
class Post:
    """"""


@app.resource('/topics/<int:topic_id>/posts/<int:post_id>/comments')
class Comments:
