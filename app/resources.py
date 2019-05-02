from flask_restful import Resource, request
from sqlalchemy.exc import IntegrityError
from app.models import User, Feedback
from app import db, jwt
from app.errors import EmailAlreadyInUse, UserDNE, PasswordIncorrect
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from app.util import (add_token_to_database, is_token_revoked, revoke_token)


class UserRegistrationEndpoint(Resource):
    def post(self):
        user_json = request.get_json()
        if User.query.filter_by(email=user_json['email']).first() is not None:
            raise EmailAlreadyInUse()
        user = User(user_json['first_name'], user_json['last_name'],
                    user_json['email'], user_json['password'])
        db.session.add(user)
        db.session.commit()
        return {'msg': 'User {} created successfully'.format(user.email)}


class UserLoginEndpoint(Resource):
    def post(self):
        email_and_pwd_json = request.get_json()
        email = email_and_pwd_json['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            raise UserDNE(email)
        if user.check_password(email_and_pwd_json['password']):
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
    def post(self):
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
    def post(self):
        feedback_json = request.get_json()
        feedback = Feedback(name=feedback_json['name'],
                            email=feedback_json['email'],
                            text=feedback_json['text'])
        db.session.add(feedback)
        db.session.commit()
        return {'msg': 'Feedback submitted'}


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


class UserLogoutAccess(Resource):
    def post(self):
        return {'msg': 'User logout'}


class UserLogoutRefresh(Resource):
    def post(self):
        return {'msg': 'User logout'}


class TokenRefresh(Resource):
    def post(self):
        return {'msg': 'Token refresh'}


class AllUsers(Resource):
    def get(self):
        return {'msg': 'List of users'}

    def delete(self):
        return {'msg': 'Delete all users'}


class SecretResource(Resource):
    def get(self):
        return {'answer': 42}


resources_dict = {
    '/api/registration': UserRegistrationEndpoint,
    '/api/login': UserLoginEndpoint,
    '/api/account': AccountEndpoint,
    '/api/refresh': RefreshEndpoint,
    '/api/logout1': Logout1Endpoint,
    '/api/logout2': Logout2Endpoint,
    '/api/feedback': FeedbackEndpoint
}
