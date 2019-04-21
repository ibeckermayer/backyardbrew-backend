from flask import jsonify


class EmailAlreadyInUse(Exception):
    status_code = 409
    message = 'Email address already in use'

    def __init__(self):
        Exception.__init__(self)

    def to_response(self):
        response_dict = dict()
        response_dict['message'] = self.message
        response = jsonify(response_dict)
        response.status_code = self.status_code
        return response


def handle_email_already_in_use(error):
    return error.to_response()


class UserDNE(Exception):
    status_code = 404
    message = ''

    def __init__(self, email):
        Exception.__init__(self)
        self.message = 'User {} doesn\'t exist'.format(email)

    def to_response(self):
        response_dict = dict()
        response_dict['message'] = self.message
        response = jsonify(response_dict)
        response.status_code = self.status_code
        return response


def handle_user_dne(error):
    return error.to_response()


class PasswordIncorrect(Exception):
    status_code = 401
    message = ''

    def __init__(self, email):
        Exception.__init__(self)
        self.message = 'Password for user {} incorrect'.format(email)

    def to_response(self):
        response_dict = dict()
        response_dict['message'] = self.message
        response = jsonify(response_dict)
        response.status_code = self.status_code
        return response


def handle_password_incorrect(error):
    return error.to_response()
