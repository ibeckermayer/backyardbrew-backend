from flask_restful import Resource, request
from app.models import User


class UserRegistration(Resource):
    def post(self):
        # TODO: ask Josiah: should I check that the request has a json? More generally, if I check the incoming form on the frontend, is it bad practice not to check it (redundantly) on the backend? Or are there enough problems with requests that I should check to ensure it was sent properly?
        user = User.from_json(request.get_json())
        return {'message': 'User registration'}


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
