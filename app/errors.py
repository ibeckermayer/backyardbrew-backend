from flask import jsonify
from app import app


class EmailAlreadyInUse(Exception):
    status_code = 409
    message = 'email address already in use'

    def __init__(self):
        Exception.__init__(self)

    def to_response(self):
        response_dict = dict()
        response_dict['message'] = self.message
        response = jsonify(response_dict)
        response.status_code = self.status_code
        return response


@app.errorhandler(EmailAlreadyInUse)
def handle_email_already_in_use(error):
    return error.to_response()
