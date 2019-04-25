import json
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

ENDPOINT = '/api/account'


def test_no_jwt(testing_client: FlaskClient):
    '''test attempt to get account resource without jwt'''
    response = testing_client.get(ENDPOINT)

    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 401
    assert response_json['msg'] == 'Missing Authorization Header'


def test_jwt_access_valid(testing_client: FlaskClient,
                          testing_registered_user_db: SQLAlchemy):
    '''test attempt to get account resource with valid jwt access token'''
    # login as preregistered user (from testing_registered_user_db)
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')
    login_response = testing_client.post('api/login',
                                         data=json.dumps(test_data),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # get access token and build header for jwt authentication
    access_token = login_response_json['access_token']
    header = {'Authorization': 'Bearer ' + access_token}

    # ping account endpoint with access token in header
    response = testing_client.get(ENDPOINT, headers=header)

    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json['msg'] == 'Account data for User {}'.format(
        test_data['email'])
