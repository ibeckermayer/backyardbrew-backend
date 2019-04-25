'''common fixtures to be used throughout the testing suite'''
import pytest
import json
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from app import create_app, db


@pytest.fixture(scope='session')
def sess_app() -> Flask:
    '''Create app for testing session'''
    app = create_app('testing')
    return app


@pytest.fixture(scope='session')
def sess_client(sess_app: Flask) -> FlaskClient:
    '''Create test client for the testing session'''
    client = sess_app.test_client()
    ctx = sess_app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture(scope='function')
def func_empty_db() -> SQLAlchemy:
    '''Create all tables before each test and then remove all tables after each test'''
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='module')
def mod_registered_user_db(sess_client: FlaskClient) -> SQLAlchemy:
    '''create a db with a preregistered user'''
    db.create_all()
    test_data = dict(first_name='isaiah',
                     last_name='becker-mayer',
                     email='ibeckermayer@gmail.com',
                     password='test_password')
    response = sess_client.post('/api/registration',
                                data=json.dumps(test_data),
                                content_type='application/json')
    yield db
    db.session.remove()
    db.drop_all()


# @pytest.fixture(scope='function')
# def func_f
