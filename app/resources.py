from flask_restful import Resource, request
from sqlalchemy.exc import IntegrityError
from app.models import User
from app import db, api
from app.errors import EmailAlreadyInUse, UserDNE, PasswordIncorrect
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity)


class UserRegistration(Resource):
    def post(self):
        user_json = request.get_json()
        if User.query.filter_by(email=user_json['email']).first() is not None:
            raise EmailAlreadyInUse()
        user = User(user_json['first_name'], user_json['last_name'],
                    user_json['email'], user_json['password'])
        db.session.add(user)
        db.session.commit()
        return {'msg': 'User {} created successfully'.format(user.email)}


class UserLogin(Resource):
    def post(self):
        user_json = request.get_json()
        email = user_json['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            raise UserDNE(email)
        if user.check_password(user_json['password']):
            return {
                'msg': 'User {} logged in successfully'.format(user.email),
                'access_token': create_access_token(identity=user.email),
                'refresh_token': create_refresh_token(identity=user.email)
            }
        else:
            raise PasswordIncorrect(user.email)


class Account(Resource):
    @jwt_required
    def get(self):
        email = get_jwt_identity()
        return {'msg': 'Account data for User {}'.format(email)}


class Refresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        email = get_jwt_identity()
        return {
            'msg': 'Refresh successful for User {}'.format(email),
            'access_token': create_access_token(identity=email)
        }


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
    '/api/registration': UserRegistration,
    '/api/login': UserLogin,
    '/api/account': Account,
    '/api/refresh': Refresh
}
