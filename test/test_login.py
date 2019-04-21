import requests
import json

ENDPOINT = '/api/login'

# def


def test_login(session_client, module_registered_user_db):
    test_data = dict(email='ibeckermayer@gmail.com', password='test_password')

    response = session_client.post(ENDPOINT,
                                   data=json.dumps(test_data),
                                   content_type='application/json')
    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json[
        'message'] == 'User ibeckermayer@gmail.com logged in successfully'
