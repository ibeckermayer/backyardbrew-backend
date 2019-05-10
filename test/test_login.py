from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from backend import test_users, add_test_user
import requests
import json
from app.models import ROLES

ENDPOINT = '/api/login'


def test_login_success(testing_client: FlaskClient, testing_db: SQLAlchemy):
    # add test_customer to the database
    test_customer = test_users['test_customer']
    add_test_user(test_customer)

    response = testing_client.post(ENDPOINT,
                                   data=json.dumps({
                                       'email':
                                       test_customer['email'],
                                       'plaintext_password':
                                       test_customer['plaintext_password']
                                   }),
                                   content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json['msg'] == 'User {} logged in successfully'.format(
        test_customer['email'])
    assert response_json['user']['id'] == 1
    assert response_json['user']['email'] == test_customer['email']
    assert response_json['user']['first_name'] == test_customer['first_name']
    assert response_json['user']['last_name'] == test_customer['last_name']
    assert response_json['user']['role'] == test_customer['role']
    assert response_json['user'].get('access_token') != None
    assert response_json['user'].get('refresh_token') != None


def test_login_user_dne(testing_client: FlaskClient, testing_db: SQLAlchemy):
    test_customer = test_users['test_customer']

    response = testing_client.post(ENDPOINT,
                                   data=json.dumps({
                                       'email':
                                       test_customer['email'],
                                       'plaintext_password':
                                       test_customer['plaintext_password']
                                   }),
                                   content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 404
    assert response_json['msg'] == 'User {} doesn\'t exist'.format(
        test_customer['email'])
    assert response_json.get('user') == None


def test_login_wrong_pwd(testing_client: FlaskClient, testing_db: SQLAlchemy):
    # add test_customer to the database
    test_customer = test_users['test_customer']
    add_test_user(test_customer)

    response = testing_client.post(ENDPOINT,
                                   data=json.dumps({
                                       'email':
                                       test_customer['email'],
                                       'plaintext_password':
                                       'wrong_password'
                                   }),
                                   content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)
    assert status_code == 401
    assert response_json['msg'] == 'Password for user {} incorrect'.format(
        test_customer['email'])
    assert response_json.get('user') == None
