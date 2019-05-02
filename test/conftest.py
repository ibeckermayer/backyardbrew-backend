'''common fixtures to be used throughout the testing suite'''
import pytest
import json
from flask import current_app
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from app import create_app, db
from backend import reset_db
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
def testing_db() -> SQLAlchemy:
    '''Create all tables before each test and then remove all tables after each test'''
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()
