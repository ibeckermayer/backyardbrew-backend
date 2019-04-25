from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json

ENDPOINT = '/api/registration'


def test_registration(testing_client: FlaskClient,
                      testing_empty_db: SQLAlchemy):
    test_data = dict(first_name='isaiah',
                     last_name='becker-mayer',
                     email='ibeckermayer@gmail.com',
                     password='test_password')

    response = testing_client.post(ENDPOINT,
                                   data=json.dumps(test_data),
                                   content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)
    assert status_code == 200
    assert response_json[
        'msg'] == 'User ibeckermayer@gmail.com created successfully'


def test_dual_registration(testing_client: FlaskClient,
                           testing_empty_db: SQLAlchemy):
    test_data = dict(first_name='isaiah',
                     last_name='becker-mayer',
                     email='ibeckermayer@gmail.com',
                     password='test_password')

    for i in range(2):
        response = testing_client.post(ENDPOINT,
                                       data=json.dumps(test_data),
                                       content_type='application/json')
        status_code = response.status_code
        response_json = json.loads(response.data)
        if i == 0:
            assert status_code == 200
            assert response_json[
                'msg'] == 'User ibeckermayer@gmail.com created successfully'
        else:
            assert status_code == 409
            assert response_json['msg'] == 'Email address already in use'
