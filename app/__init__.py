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
    # TODO: can be optimized with an error dict, similar to resources_dict below
    app.register_error_handler(errors.EmailAlreadyInUse,
                               errors.handle_email_already_in_use)
    app.register_error_handler(errors.UserDNE, errors.handle_user_dne)
    app.register_error_handler(errors.PasswordIncorrect,
                               errors.handle_password_incorrect)

    # register db
    db.init_app(app)

    # register migration
    migrate.init_app(app, db)

    # register api resources
    for path, resourceObj in resources.resources_dict.items():
        api.add_resource(resourceObj, path)

    # initialize api
    api.init_app(app)

    return app
