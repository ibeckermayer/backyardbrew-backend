'''Exceptions for errors in requests. This is simply a more elegant, object-oriented way to handle errors in flask; they could alternatively be hardcoded within the resources. Errors and handlers are registered in the create_app() function in app/__init__.py via app.register_error_handler()'''
from flask import jsonify


class EmailAlreadyInUse(Exception):
    status_code = 409
    msg = 'Email address already in use'

    def __init__(self):
        Exception.__init__(self)

    def to_response(self) -> dict:
        response_dict = dict()
        response_dict['msg'] = self.msg
        response = jsonify(response_dict)
        response.status_code = self.status_code
        return response


def handle_email_already_in_use(error: Exception) -> dict:
    return error.to_response()


class UserDNE(Exception):
    status_code = 404
    msg = ''

    def __init__(self, email: str):
        Exception.__init__(self)
        self.msg = 'User {} doesn\'t exist'.format(email)

    def to_response(self) -> dict:
        response_dict = dict()
        response_dict['msg'] = self.msg
        response = jsonify(response_dict)
        response.status_code = self.status_code
        return response


def handle_user_dne(error: Exception) -> dict:
    return error.to_response()


class UserNotAdmin(Exception):
    '''
    error for when user tries to access administrator endpoint without admin privileges
    '''
    status_code = 401
    msg = ''

    def __init__(self, email: str):
        Exception.__init__(self)
        self.msg = 'User {} does not have admin privileges'.format(email)

    def to_response(self) -> dict:
        response_dict = dict()
        response_dict['msg'] = self.msg
        response = jsonify(response_dict)
        response.status_code = self.status_code
        return response


def handle_user_not_admin(error: Exception) -> dict:
    return error.to_response()


class PasswordIncorrect(Exception):
    status_code = 401
    msg = ''

    def __init__(self, email: str):
        Exception.__init__(self)
        self.msg = 'Password for user {} incorrect'.format(email)

    def to_response(self) -> dict:
        response_dict = dict()
        response_dict['msg'] = self.msg
        response = jsonify(response_dict)
        response.status_code = self.status_code
        return response


def handle_password_incorrect(error: Exception) -> dict:
    return error.to_response()


class TokenNotFound(Exception):
    """
    Indicates that a token could not be found in the database
    """
    pass
