from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json

ENDPOINT = 'api/fullcatalog'


def test_all_item(testing_client: FlaskClient, testing_db: SQLAlchemy):
    CATEGORIES = ['Coffee', 'Black Tea',
                  'Brew']  # list of all the categories so far
    response = testing_client.get(ENDPOINT)
    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert response_json['msg'] == 'Items retrieved'
    for item in response_json['items']:
        assert item[
            'image_url'] != None  # check that all items have an associated image_url
        assert item[
            'category_data'] != None  # check that all items have an associated category_data
    for cat in response_json['categories']:
        assert cat['name'] in CATEGORIES
