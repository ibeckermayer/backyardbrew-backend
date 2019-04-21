import requests
import json

ENDPOINT = '/api/login'


def test_login_success(session_client, module_registered_user_db):
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')

    response = session_client.post(ENDPOINT,
                                   data=json.dumps(test_data),
                                   content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json[
        'message'] == 'User ibeckermayer@gmail.com logged in successfully'


def test_login_user_dne(session_client, module_registered_user_db):
    test_data = dict(email='dne@gmail.com', password='test_password')

    response = session_client.post(ENDPOINT,
                                   data=json.dumps(test_data),
                                   content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 404
    assert response_json['message'] == 'User dne@gmail.com doesn\'t exist'


def test_login_wrong_pwd(session_client, module_registered_user_db):
    test_data = dict(email='ibeckermayer@gmail.com', password='wrong_password')

    response = session_client.post(ENDPOINT,
                                   data=json.dumps(test_data),
                                   content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)
    assert status_code == 401
    assert response_json[
        'message'] == 'Password for user ibeckermayer@gmail.com incorrect'
