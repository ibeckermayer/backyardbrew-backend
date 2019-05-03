import os
from app import create_app, db
from app.models import ROLES, User, Feedback
from flask_sqlalchemy import SQLAlchemy
import random
import string
import lorem

config_name = os.getenv('APP_SETTINGS')  # config_name = "development"
app = create_app(config_name)
'''
The following are data structures and functions for use in flask shell and testing
'''


def random_lorem() -> str:
    '''
    randomly generate one of lorem.sentence(), lorem.paragraph(), or lorem.text()
    '''
    choices = ['sentence', 'paragraph', 'text']
    choice = random.choice(choices)
    if (choice == 'sentence'):
        return lorem.sentence()
    elif (choice == 'paragraph'):
        return lorem.paragraph()
    else:
        return lorem.text()


def random_string(stringLength=10) -> str:
    '''
    Generate a random string of fixed length
    '''
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


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
'''
15 resolved feedback examples as a list of dict
'''
test_feedback_resolved = [{
    'name': random_string(),
    'email': random_string() + '@feedback.com',
    'text': random_lorem(),
    'resolved': True
} for i in range(15)]
'''
15 unresolved feedback examples as a list of dict
'''
test_feedback_unresolved = [{
    'name': random_string(),
    'email': random_string() + '@feedback.com',
    'text': random_lorem(),
    'resolved': False
} for i in range(15)]


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


def add_test_feedback(test_feedback: dict):
    '''
    adds a test_feedback object to the database
    '''
    feedback = Feedback(name=test_feedback['name'],
                        email=test_feedback['email'],
                        text=test_feedback['text'],
                        resolved=test_feedback['resolved'])
    feedback.save_new()


def add_all_test_feedback():
    '''
    add all 15 resolved and unresolved test feedback examples to the database
    '''
    for fb in test_feedback_resolved:
        add_test_feedback(fb)

    for fb in test_feedback_unresolved:
        add_test_feedback(fb)


@app.shell_context_processor
def make_shell_context():
    return {
        'config_name': config_name,
        'db': db,
        'reset_db': reset_db,
        'test_users': test_users,
        'add_test_user': add_test_user,
        'add_test_customer': add_test_customer,
        'add_test_admin': add_test_admin,
        'random_string': random_string,
        'random_lorem': random_lorem,
        'test_feedback_resolved': test_feedback_resolved,
        'test_feedback_unresolved': test_feedback_unresolved,
        'add_test_feedback': add_test_feedback,
        'add_all_test_feedback': add_all_test_feedback,
        'Feedback': Feedback,
        'User': User
    }
