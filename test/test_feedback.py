from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json

ENDPOINT = '/api/feedback'


def test_submit_feedback(testing_client: FlaskClient,
                         testing_empty_db: SQLAlchemy):
    '''
    test feedback is submitted successfully
    '''
    test_data = dict(
        name='Isaiah Becker-Mayer',
        email='ibeckermayer@gmail.com',
        text=
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Elementum curabitur vitae nunc sed velit dignissim. Eget felis eget nunc lobortis mattis aliquam faucibus. Odio aenean sed adipiscing diam donec adipiscing tristique risus. Turpis massa sed elementum tempus egestas sed sed risus. Massa enim nec dui nunc mattis enim ut tellus. Tempus urna et pharetra pharetra massa. Ultricies mi quis hendrerit dolor magna. Urna porttitor rhoncus dolor purus non enim praesent elementum facilisis. Pharetra pharetra massa massa ultricies mi quis hendrerit dolor. Malesuada fames ac turpis egestas integer eget. Ac feugiat sed lectus vestibulum. Commodo ullamcorper a lacus vestibulum sed arcu. Sed turpis tincidunt id aliquet risus feugiat in. Arcu bibendum at varius vel pharetra vel turpis.'
    )

    response = testing_client.post(ENDPOINT,
                                   data=json.dumps(test_data),
                                   content_type='application/json')

    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json['msg'] == 'Feedback submitted'
