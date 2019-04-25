from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json

ENDPOINT = '/api/login'


def test_login_success(sess_client: FlaskClient,
                       mod_registered_user_db: SQLAlchemy):
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')

    response = sess_client.post(ENDPOINT,
                                data=json.dumps(test_data),
                                content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json[
        'msg'] == 'User ibeckermayer@gmail.com logged in successfully'
    assert response_json.get('access_token') != None


def test_login_user_dne(sess_client: FlaskClient,
                        mod_registered_user_db: SQLAlchemy):
    test_data = dict(email='dne@gmail.com', password='test_password')

    response = sess_client.post(ENDPOINT,
                                data=json.dumps(test_data),
                                content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 404
    assert response_json['msg'] == 'User dne@gmail.com doesn\'t exist'


def test_login_wrong_pwd(sess_client: FlaskClient,
                         mod_registered_user_db: SQLAlchemy):
    test_data = dict(email='ibeckermayer@gmail.com', password='wrong_password')

    response = sess_client.post(ENDPOINT,
                                data=json.dumps(test_data),
                                content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)
    assert status_code == 401
    assert response_json[
        'msg'] == 'Password for user ibeckermayer@gmail.com incorrect'
