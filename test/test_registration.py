import pytest
import requests
import json
from app import create_app, db
from app.resources import resources_dict

ENDPOINT = '/api/registration'


@pytest.fixture(scope='module')
def test_client():
    '''Create app and test client for the module'''
    # create app with testing config
    app = create_app('testing')
    client = app.test_client()
    # create and push onto context
    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture(scope='function')
def test_db():
    '''Create all tables before each test and then remove all tables after each test'''
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


def test_registration(test_client, test_db):
    test_data = dict(first_name='isaiah',
                     last_name='becker-mayer',
                     email='ibeckermayer@gmail.com',
                     password='test_password')

    response = test_client.post(ENDPOINT,
                                data=json.dumps(test_data),
                                content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)
    assert status_code == 200
    assert response_json[
        'message'] == 'User ibeckermayer@gmail.com created successfully'


def test_dual_registration(test_client, test_db):
    test_data = dict(first_name='isaiah',
                     last_name='becker-mayer',
                     email='ibeckermayer@gmail.com',
                     password='test_password')

    for i in range(2):
        response = test_client.post(ENDPOINT,
                                    data=json.dumps(test_data),
                                    content_type='application/json')
        status_code = response.status_code
        response_json = json.loads(response.data)
        if i == 0:
            assert status_code == 200
            assert response_json[
                'message'] == 'User ibeckermayer@gmail.com created successfully'
        else:
            assert status_code == 409
            assert response_json['message'] == 'Email address already in use'
