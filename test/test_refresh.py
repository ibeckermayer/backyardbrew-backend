from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from time import sleep
from dateutil import relativedelta
from backend import test_users, add_test_user

ENDPOINT = '/api/refresh'


def test_refresh_valid(testing_client: FlaskClient, testing_db: SQLAlchemy):
    # add test_customer to the database
    test_customer = test_users['test_customer']
    add_test_user(test_customer)

    # login
    login_response = testing_client.post(
        '/api/login',
        data=json.dumps({
            'email':
            test_customer['email'],
            'plaintext_password':
            test_customer['plaintext_password']
        }),
        content_type='application/json')

    # get refresh token and create header
    login_response_json = json.loads(login_response.data)
    refresh_token = login_response_json['user']['refresh_token']
    header = {'Authorization': 'Bearer ' + refresh_token}

    # ask for new access token from refresh endpoint
    response = testing_client.put(ENDPOINT, headers=header)

    response_json = json.loads(response.data)
    status_code = response.status_code
    msg = response_json['msg']
    access_token = response_json.get('access_token')

    # assert that this works according to plan
    assert status_code == 200
    assert msg == 'Refresh successful for User {}'.format(
        test_customer['email'])
    assert access_token != None

    # check that new access_token works properly
    header = {'Authorization': 'Bearer ' + access_token}
    account_response = testing_client.get('/api/account', headers=header)
    status_code = account_response.status_code
    account_response_json = json.loads(account_response.data)

    assert status_code == 200
    assert account_response_json['msg'] == 'Account data for User {}'.format(
        test_customer['email'])


def test_jwt_refresh_expired(testing_client: FlaskClient,
                             testing_db: SQLAlchemy):
    # set both access_token and refresh_token to expire quickly
    testing_client.application.config[
        'JWT_ACCESS_TOKEN_EXPIRES'] = relativedelta.relativedelta(
            microseconds=1)  # access token expires in 1 microsecond (minimum)
    testing_client.application.config[
        'JWT_REFRESH_TOKEN_EXPIRES'] = relativedelta.relativedelta(
            microseconds=1)  # refresh token expires in 1 microsecond (minimum)

    # add test_customer to the database
    test_customer = test_users['test_customer']
    add_test_user(test_customer)

    # login
    login_response = testing_client.post(
        '/api/login',
        data=json.dumps({
            'email':
            test_customer['email'],
            'plaintext_password':
            test_customer['plaintext_password']
        }),
        content_type='application/json')

    # get refresh token and create header
    login_response_json = json.loads(login_response.data)
    refresh_token = login_response_json['user']['refresh_token']
    header = {'Authorization': 'Bearer ' + refresh_token}

    sleep(1.1)  # sleep for 1.1 second to allow token to expire

    # ask for new access token from refresh endpoint
    response = testing_client.put(ENDPOINT, headers=header)

    # should fail
    response_json = json.loads(response.data)
    # assert response.status_code == 401
    assert response_json['msg'] == 'Token has expired'
