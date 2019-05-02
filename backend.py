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


def add_test_user(test_user: dict):
    '''
    Add a user from test_users to the database
    '''
    user = User(first_name=test_user['first_name'],
                last_name=test_user['last_name'],
                email=test_user['email'],
                plaintext_password=test_user['plaintext_password'],
                role=test_user['role'])
    user.save_new()


def add_test_customer():
    '''
    add test_users['test_customer'] to the database
    '''
    add_test_user(test_users['test_customer'])


def add_test_admin():
    '''
    add test_users['test_admin'] to the database
    '''
    add_test_user(test_users['test_admin'])


@app.shell_context_processor
def make_shell_context():
    return {
        'config_name': config_name,
        'db': db,
        'reset_db': reset_db,
        'test_users': test_users,
        'add_test_user': add_test_user,
        'add_test_customer': add_test_customer,
        'add_test_admin': add_test_admin
    }
