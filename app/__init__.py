from flask import Flask
from config import app_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api

db = SQLAlchemy()
migrate = Migrate()
api = Api()


def create_app(config_name):
    # imports
    from app import resources
    from app import errors

    # configure app
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])

    # register error handlers
    app.register_error_handler(errors.EmailAlreadyInUse,
                               errors.handle_email_already_in_use)

    # register db
    db.init_app(app)

    # register migration
    migrate.init_app(app, db)

    # register api resources
    api.add_resource(resources.UserRegistration, '/registration')
    api.add_resource(resources.UserLogin, '/login')
    api.add_resource(resources.UserLogoutAccess, '/logout/access')
    api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
    api.add_resource(resources.TokenRefresh, '/token/refresh')
    api.add_resource(resources.AllUsers, '/users')
    api.add_resource(resources.SecretResource, '/secret')

    # initialize api
    api.init_app(app)

    return app
