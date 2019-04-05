from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)  # configure app from Config obj
db = SQLAlchemy(app)            # initialize database for app
migrate = Migrate(app, db)      # initialize migration manager for app + db

from app import routes, models
