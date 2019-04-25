'''common fixtures to be used throughout the testing suite'''
import pytest
import json
from flask import Flask, current_app
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from app import create_app, db


@pytest.fixture
def testing_app() -> Flask:
    '''Create app for testing session'''
    app = create_app('testing')
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture
def testing_client(testing_app: Flask) -> FlaskClient:
    '''Create test client for the testing session'''
    client = testing_app.test_client()
    return client


@pytest.fixture
def testing_empty_db(testing_app: Flask) -> SQLAlchemy:
    '''Create all tables before each test and then remove all tables after each test'''
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture
def testing_registered_user_db(testing_client: FlaskClient) -> SQLAlchemy:
    '''create a db with a preregistered user'''
    db.create_all()
    test_data = dict(first_name='isaiah',
                     last_name='becker-mayer',
                     email='ibeckermayer@gmail.com',
                     password='test_password')
    response = testing_client.post('/api/registration',
                                   data=json.dumps(test_data),
                                   content_type='application/json')
    yield db
    db.session.remove()
    db.drop_all()
