import os
from app import create_app, db
from flask_sqlalchemy import SQLAlchemy

config_name = os.getenv('APP_SETTINGS')  # config_name = "development"
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'reset_db': reset_db}


def reset_db(db: SQLAlchemy):
    '''
    Function to reset the database from the flask shell.
    '''
    db.drop_all()
    db.create_all()
