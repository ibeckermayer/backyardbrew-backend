from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import lorem

ENDPOINT = '/api/feedback'


def test_submit_feedback(testing_client: FlaskClient, testing_db: SQLAlchemy):
    '''
    test feedback is submitted successfully
    '''
    test_data = dict(name='Isaiah Becker-Mayer',
                     email='ibeckermayer@gmail.com',
                     text=lorem.text())

    response = testing_client.post(ENDPOINT,
                                   data=json.dumps(test_data),
                                   content_type='application/json')

    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json['msg'] == 'Feedback submitted'
