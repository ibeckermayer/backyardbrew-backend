from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from time import sleep

ENDPOINT = '/api/refresh'


def test_refresh_valid(testing_client: FlaskClient,
                       testing_registered_user_db: SQLAlchemy):
    # login
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')
    login_response = testing_client.post('/api/login',
                                         data=json.dumps(test_data),
                                         content_type='application/json')
    # get refresh token and create header
    login_response_json = json.loads(login_response.data)
    refresh_token = login_response_json['refresh_token']
    header = {'Authorization': 'Bearer ' + refresh_token}

    # ask for new access token from refresh endpoint
    response = testing_client.post(ENDPOINT, headers=header)

    response_json = json.loads(response.data)
    status_code = response.status_code
    msg = response_json['msg']
    access_token = response_json.get('access_token')

    # assert that this works according to plan
    assert status_code == 200
    assert msg == 'Refresh successful for User {}'.format(test_data['email'])
    assert access_token != None

    # check that new access_token works properly
    header = {'Authorization': 'Bearer ' + access_token}
    account_response = testing_client.get('/api/account', headers=header)
    status_code = account_response.status_code
    account_response_json = json.loads(account_response.data)

    assert status_code == 200
    assert account_response_json['msg'] == 'Account data for User {}'.format(
        test_data['email'])


def test_refresh_expired(testing_refresh_exp_client: FlaskClient,
                         testing_refresh_exp_registered_user_db: SQLAlchemy):
    # login
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')
    login_response = testing_refresh_exp_client.post(
        '/api/login',
        data=json.dumps(test_data),
        content_type='application/json')
    # get refresh token and create header
    login_response_json = json.loads(login_response.data)
    refresh_token = login_response_json['refresh_token']
    header = {'Authorization': 'Bearer ' + refresh_token}

    sleep(1.1)  # sleep for 1.1 second to allow token to expire

    # ask for new access token from refresh endpoint
    response = testing_refresh_exp_client.post(ENDPOINT, headers=header)

    # should fail
    response_json = json.loads(response.data)
    # assert response.status_code == 401
    assert response_json['msg'] == 'Token has expired'
