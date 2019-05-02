'''common fixtures to be used throughout the testing suite'''
import pytest
import json
from flask import current_app
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from app import create_app, db
from app.models import User, ROLES
import random
import string


@pytest.fixture
def testing_client() -> FlaskClient:
    '''Create app for testing session'''
    app = create_app('testing')
    ctx = app.app_context()
    ctx.push()
    yield app.test_client()
    ctx.pop()


@pytest.fixture
def testing_jwt_access_exp_client() -> FlaskClient:
    '''create app with immediate jwt access expiration config to test jwt expiration'''
    app = create_app('jwt_access_immediate_expire_test')
    ctx = app.app_context()
    ctx.push()
    yield app.test_client()
    ctx.pop()


@pytest.fixture
def testing_jwt_refresh_exp_client() -> FlaskClient:
    '''create app with immediate jwt access expiration config to test jwt expiration'''
    app = create_app('jwt_refresh_immediate_expire_test')
    ctx = app.app_context()
    ctx.push()
    yield app.test_client()
    ctx.pop()


@pytest.fixture
def testing_empty_db() -> SQLAlchemy:
    '''Create all tables before each test and then remove all tables after each test'''
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture
def testing_registered_user_db() -> SQLAlchemy:
    '''create a db with a preregistered user'''
    db.create_all()
    user = User(first_name='isaiah',
                last_name='becker-mayer',
                email='ibeckermayer@gmail.com',
                plaintext_password='test_password')
    db.session.add(user)
    db.session.commit()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture
def testing_registered_user_and_admin_user_db(
        testing_registered_user_db: SQLAlchemy) -> SQLAlchemy:
    '''create db with preregistered user and preregistered admin user'''
    admin_user = User(first_name='admin',
                      last_name='user',
                      email='admin@admin.com',
                      plaintext_password='adminuser')

    admin_user.role = ROLES['admin']
    testing_registered_user_db.add(admin_user)
    testing_registered_user_db.commit()
    return testing_registered_user_db
