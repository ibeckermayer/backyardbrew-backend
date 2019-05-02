import os
from app import create_app, db
from app.models import ROLES, User, Feedback
from flask_sqlalchemy import SQLAlchemy

config_name = os.getenv('APP_SETTINGS')  # config_name = "development"
app = create_app(config_name)
'''
The following are data structures and functions for use in flask shell and testing
'''
test_users = {
    'test_customer': {
        'first_name': 'test',
        'last_name': 'customer',
        'email': 'test@customer.com',
        'plaintext_password': 'test_customer',
        'role': ROLES['customer']
    },
    'test_admin': {
        'first_name': 'test',
        'last_name': 'admin',
        'email': 'test@admin.com',
        'plaintext_password': 'test_admin',
        'role': ROLES['admin']
    }
}


def reset_db():
    '''
    Function to reset the database from the flask shell.
    '''
    db.drop_all()
    db.create_all()


def populate_test_customer(db: SQLAlchemy):
    '''
    Add a test_customer to the database
    '''
    pass


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'reset_db': reset_db}
