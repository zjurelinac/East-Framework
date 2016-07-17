EAST (pf) - Easy REST Python Framework
================================================================================
_Inspired by Flask, Flask-RESTful and clever ideas from around the web_

Features:
    - Resource-based API or simple, view-function based (both supported)
        - @app.resource, @app.route decorators
    - Type hinting for parameter detection and return type
        - JSON, HTML, XML, file, str and other response formatters
    - Parameter validation
        - Defined globally, possible turning on/off
        - Defined on an input type -> combined parsing & validation
    - Do everything locally, inside the app object (configuration) or inside request Context
    - **Enable setting response headers inside a view**
    - **What about status codes?**
    - **Allow templating via HTML return type?**
    - **API user input parameter == authentication?**
    - **Cache common properties**
    - **Implement OPTIONS response by default**

Notes:
    - Think about extending JSON to handle input as well
    - Introduce safety measures - output escaping for HTML etc.
    - Think about default route parameter values - are they neccessary?
    - Check return format, is accepted by the client?
    - Check view returns for status code to avoid errors

Workflow:
    + _Create TODO example app_
    + _Create Resource class and other user-oriented features (decorators etc.)_
    + _Implement routing_
    + _Implement Context class functionalities_
    + _Create utility classes - variants of dict_
    + _Implement request parsing (basics)_
    + _Implement response generation_
    + _Implement exception handling_
    - Implement logging
    + _Think through preprocessing & postprocessing, security_
    - Enable testing
    - Implement further request parsing functionalities
    - Create an example project - simplest of blogs - Topic, Post, Comment

Usage example:

    @app.route('/')
    class UserResource(Resource):
        
        def get(self, id: int) -> JSON:
            return User.get(User.id == id)

        def put(self, id: int, username: str, password: str, email:str) -> JSON:
            user = User.get(User.id)
            user.update(username = username, password = password, email = email).save()
            return user

