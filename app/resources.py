from flask_restful import Resource, request
from sqlalchemy.exc import IntegrityError
from app.models import User, Feedback
from app import db, jwt
from app.errors import EmailAlreadyInUse, UserDNE, PasswordIncorrect, UserNotAdmin
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from app.util import (add_token_to_database, is_token_revoked, revoke_token)


class UserRegistrationEndpoint(Resource):
    def put(self):
        user_json = request.get_json()
        if User.get(user_json['email']) is not None:
            raise EmailAlreadyInUse()
        user = User(first_name=user_json['first_name'],
                    last_name=user_json['last_name'],
                    email=user_json['email'],
                    plaintext_password=user_json['plaintext_password'])
        user.save_new()
        return {'msg': 'User {} created successfully'.format(user.email)}


class UserLoginEndpoint(Resource):
    def post(self):
        email_and_pwd_json = request.get_json()
        email = email_and_pwd_json['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            raise UserDNE(email)
        if user.check_password(email_and_pwd_json['plaintext_password']):
            # create jwt
            access_token = create_access_token(identity=user.email)
            refresh_token = create_refresh_token(identity=user.email)

            # Store the tokens in our store with a status of not currently revoked.
            add_token_to_database(access_token)
            add_token_to_database(refresh_token)

            return {
                'msg': 'User {} logged in successfully'.format(user.email),
                'user': user.to_json(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            raise PasswordIncorrect(user.email)


class AccountEndpoint(Resource):
    @jwt_required
    def get(self):
        email = get_jwt_identity()
        return {'msg': 'Account data for User {}'.format(email)}


class RefreshEndpoint(Resource):
    @jwt_refresh_token_required
    def put(self):
        email = get_jwt_identity()
        access_token = create_access_token(identity=email)
        add_token_to_database(access_token)
        return {
            'msg': 'Refresh successful for User {}'.format(email),
            'access_token': access_token
        }


class Logout1Endpoint(Resource):
    @jwt_required
    def delete(self):
        revoke_token(get_raw_jwt())
        return {'msg': 'JWT access token revoked'}


class Logout2Endpoint(Resource):
    @jwt_refresh_token_required
    def delete(self):
        revoke_token(get_raw_jwt())
        return {'msg': 'JWT refresh token revoked'}


class FeedbackEndpoint(Resource):
    def put(self):
        '''
        submit new piece of feedback
        '''
        feedback_json = request.get_json()
        feedback = Feedback(name=feedback_json['name'],
                            email=feedback_json['email'],
                            text=feedback_json['text'])
        feedback.save_new()
        return {'msg': 'Feedback submitted'}

    @jwt_required
    def post(self):
        '''
        get a page of either resolved or unresolved feedback
        '''
        email = get_jwt_identity()
        if User.is_admin(email):
            req_json = request.get_json()
            resolved = req_json['resolved']
            page = req_json['page']
            return {
                'feedbacks': [
                    fb.to_json()
                    for fb in Feedback.get(resolved=resolved, page=page)
                ]
            }
        else:
            raise UserNotAdmin(email)

    @jwt_required
    def patch(self):
        '''
        update resolved flag on a feedback object, given by id
        NOTE: Do not simply toggle the resolved column of the object. If multiple admins are logged in going through
        feedback, a toggle could possibly result in a piece of feedback being marked incorrectly depending on
        the 'phase difference' between when their respective frontends were last updated on the backend.
        '''
        email = get_jwt_identity()
        if User.is_admin(email):
            req_json = request.get_json()
            id = req_json['id']  # specifies which feedback object to edit
            resolved = req_json[
                'resolved']  # states whether the item should be marked resolved or unresolved
            Feedback.set_resolved(id, resolved)
            return {
                'msg':
                'Feedback object {} resolved attribute set to {}'.format(
                    id, resolved)
            }
        else:
            raise UserNotAdmin(email)


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


resources_dict = {
    '/api/registration': UserRegistrationEndpoint,
    '/api/login': UserLoginEndpoint,
    '/api/account': AccountEndpoint,
    '/api/refresh': RefreshEndpoint,
    '/api/logout1': Logout1Endpoint,
    '/api/logout2': Logout2Endpoint,
    '/api/feedback': FeedbackEndpoint
}
