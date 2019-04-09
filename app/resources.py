from flask_restful import Resource, request
from sqlalchemy.exc import IntegrityError
from app.models import User
from app import db, api
from app.errors import EmailAlreadyInUse


class UserRegistration(Resource):
    def post(self):
        user = User.from_json(request.get_json())
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            raise EmailAlreadyInUse()
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
