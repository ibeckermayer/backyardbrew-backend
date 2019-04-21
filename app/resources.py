from flask_restful import Resource, request
from sqlalchemy.exc import IntegrityError
from app.models import User
from app import db, api
from app.errors import EmailAlreadyInUse


class UserRegistration(Resource):
    def post(self):
        user_json = request.get_json()
        if User.query.filter_by(email=user_json['email']).first() is not None:
            raise EmailAlreadyInUse()
        user = User(user_json['first_name'], user_json['last_name'],
                    user_json['email'], user_json['password'])
        db.session.add(user)
        db.session.commit()
        return {'message': 'User {} created successfully'.format(user.email)}


class UserLogin(Resource):
    def post(self):
        return {'message': 'User login'}


class UserLogoutAccess(Resource):
    def post(self):
        return {'message': 'User logout'}


class UserLogoutRefresh(Resource):
    def post(self):
        return {'message': 'User logout'}


class TokenRefresh(Resource):
    def post(self):
        return {'message': 'Token refresh'}


class AllUsers(Resource):
    def get(self):
        return {'message': 'List of users'}

    def delete(self):
        return {'message': 'Delete all users'}


class SecretResource(Resource):
    def get(self):
        return {'answer': 42}


resources_dict = {
    '/api/registration': UserRegistration,
    '/api/login': UserLogin
}
