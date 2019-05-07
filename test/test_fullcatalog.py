from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json

ENDPOINT = 'api/fullcatalog'


def test_all_item(testing_client: FlaskClient, testing_db: SQLAlchemy):
    # set body to ask api for all items
    data = json.dumps({"body": {"object_types": ["ITEM"]}})

    response = testing_client.get(ENDPOINT)
    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert response_json['msg'] == 'Items retrieved'
    for item in response_json['items']:
        assert item['image_url'] != None
