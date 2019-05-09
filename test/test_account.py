import json
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from time import sleep
from dateutil import relativedelta
from backend import test_users, add_test_user

ENDPOINT = '/api/account'


def test_no_jwt(testing_client: FlaskClient):
    '''test attempt to get account resource without jwt'''
    response = testing_client.get(ENDPOINT)

    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 401
    assert response_json['msg'] == 'Missing Authorization Header'


def test_jwt_access_valid(testing_client: FlaskClient, testing_db: SQLAlchemy):
    '''test attempt to get account resource with valid jwt access token'''
    # add test_customer to the database
    test_customer = test_users['test_customer']
    add_test_user(test_customer)

    login_response = testing_client.post(
        'api/login',
        data=json.dumps({
            'email':
            test_customer['email'],
            'plaintext_password':
            test_customer['plaintext_password']
        }),
        content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # get access token and build header for jwt authentication
    access_token = login_response_json['user']['access_token']
    header = {'Authorization': 'Bearer ' + access_token}

    # ping account endpoint with access token in header
    response = testing_client.get(ENDPOINT, headers=header)

    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json['msg'] == 'Account data for User {}'.format(
        test_customer['email'])


def test_jwt_access_expired(testing_client: FlaskClient,
                            testing_db: SQLAlchemy):

    # set access_token to expire quickly
    testing_client.application.config[
        'JWT_ACCESS_TOKEN_EXPIRES'] = relativedelta.relativedelta(
            microseconds=1)  # access token expires in 1 microsecond (minimum)

    # add test_customer to the database
    test_customer = test_users['test_customer']
    add_test_user(test_customer)

    # login as test_customer
    login_response = testing_client.post(
        'api/login',
        data=json.dumps({
            'email':
            test_customer['email'],
            'plaintext_password':
            test_customer['plaintext_password']
        }),
        content_type='application/json')

    sleep(1.1)  # sleep for 1.1 second to allow token to expire

    login_response_json = json.loads(login_response.data)

    # get access token and build header for jwt authentication
    access_token = login_response_json['user']['access_token']
    header = {'Authorization': 'Bearer ' + access_token}

    # ping account endpoint with access token in header
    response = testing_client.get(ENDPOINT, headers=header)

    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 401
    assert response_json['msg'] == 'Token has expired'
