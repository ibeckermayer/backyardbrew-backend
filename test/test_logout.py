from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from time import sleep

LOGOUT1 = '/api/logout1'
LOGOUT2 = '/api/logout2'


def test_logout_both_valid(testing_client: FlaskClient,
                           testing_registered_user_db: SQLAlchemy):
    '''
    test logging out with both access and refresh jwt valid
    '''
    # login
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')
    login_response = testing_client.post('/api/login',
                                         data=json.dumps(test_data),
                                         content_type='application/json')
    login_response_json = json.loads(login_response.data)

    # extract tokens
    access_token = login_response_json['access_token']
    refresh_token = login_response_json['refresh_token']

    # ping logout1 to revoke access token
    access_header = {'Authorization': 'Bearer ' + access_token}
    logout1_response = testing_client.delete(LOGOUT1, headers=access_header)
    logout1_response_json = json.loads(logout1_response.data)
    assert logout1_response.status_code == 200
    assert logout1_response_json['msg'] == 'JWT access token revoked'

    # check that access token no longer gives access to account endpoint
    account_response = testing_client.get('api/account', headers=access_header)
    status_code = account_response.status_code
    account_response_json = json.loads(account_response.data)
    assert status_code == 401
    assert account_response_json['msg'] == 'Token has been revoked'

    # ping logout2 to revoke access token
    refresh_header = {'Authorization': 'Bearer ' + refresh_token}
    logout2_response = testing_client.delete(LOGOUT2, headers=refresh_header)
    logout2_response_json = json.loads(logout2_response.data)
    assert logout2_response.status_code == 200
    assert logout2_response_json['msg'] == 'JWT refresh token revoked'

    # check that refresh token no longer gives access to refresh endpoint
    refresh_response = testing_client.post('api/refresh',
                                           headers=refresh_header)
    status_code = refresh_response.status_code
    refresh_response_json = json.loads(refresh_response.data)
    assert status_code == 401
    assert refresh_response_json['msg'] == 'Token has been revoked'


def test_logout_access_expired(testing_jwt_access_exp_client: FlaskClient,
                               testing_registered_user_db: SQLAlchemy):
    '''
    test logging out with access token expired but refresh token valid
    '''
    # login
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')
    login_response = testing_jwt_access_exp_client.post(
        '/api/login',
        data=json.dumps(test_data),
        content_type='application/json')
    login_response_json = json.loads(login_response.data)
    sleep(1.1)  # sleep for 1.1 second to allow access_token to expire

    # extract tokens
    access_token = login_response_json['access_token']
    refresh_token = login_response_json['refresh_token']

    # ping logout1 to revoke access token, but expect token to be expired
    # NOTE: token is not revoked, since its already expired
    access_header = {'Authorization': 'Bearer ' + access_token}
    logout1_response = testing_jwt_access_exp_client.delete(
        LOGOUT1, headers=access_header)
    logout1_response_json = json.loads(logout1_response.data)
    assert logout1_response.status_code == 401
    assert logout1_response_json['msg'] == 'Token has expired'

    # check that access token no longer gives access to account endpoint
    # NOTE: in contrast to a token that has been revoked, this call will tell you the token has expired
    account_response = testing_jwt_access_exp_client.get('api/account',
                                                         headers=access_header)
    status_code = account_response.status_code
    account_response_json = json.loads(account_response.data)
    assert status_code == 401
    assert account_response_json['msg'] == 'Token has expired'

    # ping logout2 to revoke access token
    refresh_header = {'Authorization': 'Bearer ' + refresh_token}
    logout2_response = testing_jwt_access_exp_client.delete(
        LOGOUT2, headers=refresh_header)
    logout2_response_json = json.loads(logout2_response.data)
    assert logout2_response.status_code == 200
    assert logout2_response_json['msg'] == 'JWT refresh token revoked'

    # check that refresh token no longer gives access to refresh endpoint
    refresh_response = testing_jwt_access_exp_client.post(
        'api/refresh', headers=refresh_header)
    status_code = refresh_response.status_code
    refresh_response_json = json.loads(refresh_response.data)
    assert status_code == 401
    assert refresh_response_json['msg'] == 'Token has been revoked'


def test_logout_refresh_expired(testing_jwt_refresh_exp_client: FlaskClient,
                                testing_registered_user_db: SQLAlchemy):
    '''
    test logging out with access token expired but refresh token valid
    '''
    # login
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')
    login_response = testing_jwt_refresh_exp_client.post(
        '/api/login',
        data=json.dumps(test_data),
        content_type='application/json')
    login_response_json = json.loads(login_response.data)
    sleep(1.1)  # sleep for 1.1 second to allow access_token to expire

    # extract tokens
    access_token = login_response_json['access_token']
    refresh_token = login_response_json['refresh_token']

    # ping logout1 to revoke access token, but expect token to be expired
    # NOTE: token is not revoked, since its already expired
    access_header = {'Authorization': 'Bearer ' + access_token}
    logout1_response = testing_jwt_refresh_exp_client.delete(
        LOGOUT1, headers=access_header)
    logout1_response_json = json.loads(logout1_response.data)
    assert logout1_response.status_code == 401
    assert logout1_response_json['msg'] == 'Token has expired'

    # check that access token no longer gives access to account endpoint
    # NOTE: in contrast to a token that has been revoked, this call will tell you the token has expired
    account_response = testing_jwt_refresh_exp_client.get(
        'api/account', headers=access_header)
    status_code = account_response.status_code
    account_response_json = json.loads(account_response.data)
    assert status_code == 401
    assert account_response_json['msg'] == 'Token has expired'

    # ping logout2 to revoke access token
    # NOTE: in contrast to a token that has been revoked, this call will tell you the token has expired
    refresh_header = {'Authorization': 'Bearer ' + refresh_token}
    logout2_response = testing_jwt_refresh_exp_client.delete(
        LOGOUT2, headers=refresh_header)
    logout2_response_json = json.loads(logout2_response.data)
    assert logout2_response.status_code == 401
    assert logout2_response_json['msg'] == 'Token has expired'

    # check that refresh token no longer gives access to refresh endpoint
    refresh_response = testing_jwt_refresh_exp_client.post(
        'api/refresh', headers=refresh_header)
    status_code = refresh_response.status_code
    refresh_response_json = json.loads(refresh_response.data)
    assert status_code == 401
    assert refresh_response_json['msg'] == 'Token has expired'
