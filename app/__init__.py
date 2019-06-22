from flask import Flask
from config import app_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
api = Api()
jwt = JWTManager()
cors = CORS()


def create_app(config_name: str) -> Flask:
  '''App Factory pattern implementation. This makes it so we can create the app with different configurations
    throughout the codebase, which is especially useful for testing. '''
  # imports
  from app import resources
  from app import errors

  # configure app
  app = Flask(__name__)
  app.config.from_object(app_config[config_name])

  with app.app_context():
    # register error handlers
    # TODO: can be optimized with an error dict, similar to resources_dict below
    app.register_error_handler(errors.EmailAlreadyInUse,
                               errors.handle_email_already_in_use)
    app.register_error_handler(errors.UserDNE, errors.handle_user_dne)
    app.register_error_handler(errors.PasswordIncorrect,
                               errors.handle_password_incorrect)
    app.register_error_handler(errors.UserNotAdmin,
                               errors.handle_user_not_admin)

    # register db
    db.init_app(app)

    # register migration
    migrate.init_app(app, db)

    # register cors
    cors.init_app(app, resources={r"*": {"origins": "*"}})

    # register JWTManager
    jwt.init_app(app)

    # FlaskRestful does not integrate nicely with Flask app_context functionality.
    # Since its useful for testing purposes to be able to create multiple apps with different configurations
    # (for example, test jwt timing out requires a config with shorter jwt expiration times),
    # we are using a static variable to check whether the resources have been added to the API in this process.
    # This stops attempting to register the resources twice with the API object, which causes an error.
    if not (create_app.resources_added):
      # register api resources
      for path, resourceObj in resources.resources_dict.items():
        api.add_resource(resourceObj, path)
      create_app.resources_added = True

    # initialize api
    api.init_app(app)

  return app


# initialize creat_app.resources_added static variable
create_app.resources_added = False
