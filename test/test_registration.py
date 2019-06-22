from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json
from backend import test_users

ENDPOINT = '/api/registration'


def test_registration(testing_client: FlaskClient, testing_db: SQLAlchemy):
  test_customer = test_users['test_customer']

  response = testing_client.put(
      ENDPOINT,
      data=json.dumps({
          'first_name': test_customer['first_name'],
          'last_name': test_customer['last_name'],
          'email': test_customer['email'],
          'plaintext_password': test_customer['plaintext_password']
      }),
      content_type='application/json')
  status_code = response.status_code
  response_json = json.loads(response.data)
  assert status_code == 200
  assert response_json['msg'] == 'User {} created successfully'.format(
      test_customer['email'])


def test_dual_registration(testing_client: FlaskClient, testing_db: SQLAlchemy):
  test_customer = test_users['test_customer']

  for i in range(2):
    response = testing_client.put(
        ENDPOINT,
        data=json.dumps({
            'first_name': test_customer['first_name'],
            'last_name': test_customer['last_name'],
            'email': test_customer['email'],
            'plaintext_password': test_customer['plaintext_password']
        }),
        content_type='application/json')

    status_code = response.status_code
    response_json = json.loads(response.data)
    if i == 0:
      assert status_code == 200
      assert response_json['msg'] == 'User {} created successfully'.format(
          test_customer['email'])
    else:
      assert status_code == 409
      assert response_json['msg'] == 'Email address already in use'
