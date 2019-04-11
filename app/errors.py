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
