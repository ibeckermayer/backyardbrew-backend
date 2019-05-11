from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
import requests
import json

ENDPOINT = '/api/generate_checkout_url'


def test_generate_checkout_url(testing_client: FlaskClient):
    def create_cart_of_all_items(full_catalog: list) -> dict:
        '''
        takes in the full catalog and creates a cart with all the items
        '''
        cart = {'items': []}
        for item in full_catalog:
            for variation in item['variations']:
                cart_item = {
                    'name': item['name'],
                    'variation': variation,
                    'tax_ids': item['tax_ids'],
                    'quantity': "1"
                }
                cart['items'].append(cart_item)
        return cart

    full_cat_response = testing_client.get('api/fullcatalog')
    full_cat_response_json = json.loads(full_cat_response.data)
    cart = create_cart_of_all_items(full_cat_response_json['items'])
    # assert cart == None
    response = testing_client.post(ENDPOINT,
                                   data=json.dumps(cart),
                                   content_type='application/json')
    response_json = json.loads(response.data)

    assert response.status_code == 200
    assert response_json['msg'] == 'Checkout page created'
    assert response_json['url'] != None

    cart = json.dumps({})
