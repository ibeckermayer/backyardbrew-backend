import squareconnect
import random
import string
from typing import List
from app import db, jwt
from flask_jwt_extended import decode_token
from datetime import datetime
from app.models import TokenBlacklist
from sqlalchemy.orm.exc import NoResultFound
from squareconnect.apis import (CatalogApi, CheckoutApi, CustomersApi)
from squareconnect.models import (SearchCatalogObjectsRequest,
                                  CreateOrderRequest, CreateCheckoutRequest,
                                  Order, OrderLineItem, OrderLineItemTax,
                                  CatalogObject, CatalogItem,
                                  CreateCustomerRequest)
from config import SQUARE_ACCESS_TOKEN, SQUARE_LOCATION_ID


def gen_idem_key():
    '''
    Helper function to generate and idempotency key for use with Square's api
    '''
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase +
                                                string.digits)
                   for _ in range(50))


def _epoch_utc_to_datetime(epoch_utc: float):
    '''
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    '''
    return datetime.fromtimestamp(epoch_utc)


def add_token_to_database(encoded_token: str):
    '''
    Adds a new token to the database. It is not revoked when it is added.
    '''
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = False

    db_token = TokenBlacklist(jti=jti,
                              token_type=token_type,
                              expires=expires,
                              revoked=revoked)
    db_token.save_new()


def is_token_revoked(decoded_token: dict):
    '''
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    '''
    jti = decoded_token['jti']
    try:
        token = TokenBlacklist.query.filter_by(jti=jti).one()
        return token.revoked
    except NoResultFound:
        return True


def revoke_token(raw_token: dict):
    '''
    Revokes the given token. Raises a TokenNotFound error if the token does
    not exist in the database
    '''
    jti = raw_token['jti']
    try:
        token = TokenBlacklist.query.filter_by(jti=jti).one()
        token.revoke()
    except NoResultFound:
        raise TokenNotFound(
            "Could not find the token {}".format(encoded_token))


def prune_database():
    '''
    Delete tokens that have expired from the database.
    TODO: configure so this can be run, either manually via admin user or chron job
    '''
    now = datetime.now()
    expired = TokenBlacklist.query.filter(TokenBlacklist.expires < now).all()
    for token in expired:
        db.session.delete(token)
    db.session.commit()


def square_get_full_catalog() -> dict:
    '''
    NOTE: Super-annoying-ly, the api doesn't automatically return link ITEM catalog objects to their respective IMAGE
    This endpoint is built to grab all the ITEM's and IMAGE's, associate all the ITEM objects (copy image url in ITEM's
    image_url field) with their corresponding IMAGE and then return the ITEM list. The frontend can then store/sort/display
    this data.

    The endpoint ultimately returns a field called 'items' that is a List[squareconnect.models.catalog_item.CatalogItem].
    I modify the CatalogItem object to contain a new string field called category_data that contains the data from that
    field in its corresponding squareconnect.models.catalog_category.CatalogCategory.

    Finally the endpoint returns a field called 'catgories' which is a List[CatalogCategory] for
    use by the frontend.
    '''

    def __associate_item_data_with_image_data_url(items: List[CatalogObject],
                                                  images: List[CatalogObject]
                                                  ) -> List[CatalogObject]:
        '''
        because the square API doesn't gracefully do this for us, we manually fill out each item's
        item_data.image_url with appropriate image url
        '''
        for item in items:
            for image in images:
                if (item.image_id == image.id):
                    item.item_data.image_url = image.image_data.url
                    break
        return items

    def __associate_item_data_with_category_data(
            items: List[CatalogObject],
            categories: List[CatalogObject]) -> List[CatalogObject]:
        '''
        create new item.item_data field called category_data to associate each item with its category
        '''
        for item in items:
            for category in categories:
                if (item.item_data.category_id == category.id):
                    item.item_data.category_data = category.category_data
                    break
        return items

    def __catalog_item_to_dict(citem: CatalogItem) -> dict:
        '''
        default to_dict function for CatalogItem doesn't capture our added category_data field, so we add it to the dictionary manually
        '''
        d = citem.to_dict()
        d['category_data'] = citem.category_data.to_dict()
        return d

    api_instance = CatalogApi()
    api_instance.api_client.configuration.access_token = SQUARE_ACCESS_TOKEN
    body = SearchCatalogObjectsRequest(
        object_types=['ITEM', 'IMAGE',
                      'CATEGORY'])  # specify all ITEM, IMAGE, and CATEGORY
    itms_imgs_and_cats = api_instance.search_catalog_objects(
        body=body).objects  # List[CatalogObject]
    itms_only = list(filter(lambda obj: obj.type == 'ITEM',
                            itms_imgs_and_cats))
    imgs_only = list(
        filter(lambda obj: obj.type == 'IMAGE', itms_imgs_and_cats))
    cats_only = list(
        filter(lambda obj: obj.type == 'CATEGORY', itms_imgs_and_cats))
    itms_w_imgs = __associate_item_data_with_image_data_url(
        itms_only, imgs_only)
    itms_w_imgs_w_cats = __associate_item_data_with_category_data(
        itms_w_imgs, cats_only)
    return {
        'msg':
        'Items retrieved',
        'items': [
            __catalog_item_to_dict(item.item_data)
            for item in itms_w_imgs_w_cats
        ],  # List[CatalogItem] w/ added category_data attr
        'categories': [cat.category_data.to_dict()
                       for cat in cats_only]  # List[CatalogCategory]
    }


def square_get_checkout_url(cart: dict) -> dict:
    '''
    uses CheckoutApi to get a url to point the customer to for checkout
    '''
    # go through each item in cart and add a corresponding line_item to line_items
    line_items = []
    for item in cart['items']:
        quantity = str(item['quantity'])
        catalog_object_id = item['variation']['id']
        taxes = [
            OrderLineItemTax(catalog_object_id=tax_id)
            for tax_id in item['tax_ids']
        ]
        line_item = OrderLineItem(quantity=quantity,
                                  catalog_object_id=catalog_object_id,
                                  taxes=taxes)
        line_items.append(line_item)

    # create an order with these line_items
    order = Order(location_id=SQUARE_LOCATION_ID, line_items=line_items)

    # create an order request with this order
    order_request = CreateOrderRequest(order=order,
                                       idempotency_key=gen_idem_key())

    # create a checkout request with this order request
    body = CreateCheckoutRequest(idempotency_key=gen_idem_key(),
                                 order=order_request,
                                 ask_for_shipping_address=True)

    api_instance = CheckoutApi()
    api_instance.api_client.configuration.access_token = SQUARE_ACCESS_TOKEN
    url = api_instance.create_checkout(location_id=SQUARE_LOCATION_ID,
                                       body=body).checkout.checkout_page_url

    return {'msg': 'Checkout page created', 'url': url}


def square_create_user(given_name: str, family_name: str, email_address: str,
                       reference_id: int) -> str:
    '''
    on registration of new user, register user with square, and return the
    customer_id as given by square in order to save as cross reference in our database
    '''
    body = CreateCustomerRequest(idempotency_key=gen_idem_key(),
                                 given_name=given_name,
                                 family_name=family_name,
                                 email_address=email_address,
                                 reference_id=reference_id)
    api_instance = CustomersApi()
    api_instance.api_client.configuration.access_token = SQUARE_ACCESS_TOKEN
    return api_instance.create_customer(body=body).customer.id
