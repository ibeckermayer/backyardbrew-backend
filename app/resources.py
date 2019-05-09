from flask_restful import Resource, request
from sqlalchemy.exc import IntegrityError
from app.models import User, Feedback
from app import db, jwt
from app.errors import EmailAlreadyInUse, UserDNE, PasswordIncorrect, UserNotAdmin
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from app.util import (add_token_to_database, is_token_revoked, revoke_token)
import squareconnect
from squareconnect.apis.catalog_api import CatalogApi
from squareconnect.models import SearchCatalogObjectsRequest
from squareconnect.models.catalog_object import CatalogObject
from squareconnect.models.catalog_item import CatalogItem
from typing import List
from config import SQUARE_ACCESS_TOKEN


class UserRegistrationEndpoint(Resource):
    def put(self):
        user_json = request.get_json()
        if User.get(user_json['email']) is not None:
            raise EmailAlreadyInUse()
        user = User(first_name=user_json['first_name'],
                    last_name=user_json['last_name'],
                    email=user_json['email'],
                    plaintext_password=user_json['plaintext_password'])
        user.save_new()
        return {'msg': 'User {} created successfully'.format(user.email)}


class UserLoginEndpoint(Resource):
    def post(self):
        email_and_pwd_json = request.get_json()
        email = email_and_pwd_json['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            raise UserDNE(email)
        if user.check_password(email_and_pwd_json['plaintext_password']):
            # create jwt
            access_token = create_access_token(identity=user.email)
            refresh_token = create_refresh_token(identity=user.email)

            # Store the tokens in our store with a status of not currently revoked.
            add_token_to_database(access_token)
            add_token_to_database(refresh_token)

            return {
                'msg': 'User {} logged in successfully'.format(user.email),
                'user': user.to_json(access_token, refresh_token),
            }
        else:
            raise PasswordIncorrect(user.email)


class AccountEndpoint(Resource):
    @jwt_required
    def get(self):
        email = get_jwt_identity()
        return {'msg': 'Account data for User {}'.format(email)}


class RefreshEndpoint(Resource):
    @jwt_refresh_token_required
    def put(self):
        email = get_jwt_identity()
        access_token = create_access_token(identity=email)
        add_token_to_database(access_token)
        return {
            'msg': 'Refresh successful for User {}'.format(email),
            'access_token': access_token
        }


class Logout1Endpoint(Resource):
    @jwt_required
    def delete(self):
        revoke_token(get_raw_jwt())
        return {'msg': 'JWT access token revoked'}


class Logout2Endpoint(Resource):
    @jwt_refresh_token_required
    def delete(self):
        revoke_token(get_raw_jwt())
        return {'msg': 'JWT refresh token revoked'}


class FeedbackEndpoint(Resource):
    def put(self):
        '''
        submit new piece of feedback
        '''
        feedback_json = request.get_json()
        feedback = Feedback(name=feedback_json['name'],
                            email=feedback_json['email'],
                            text=feedback_json['text'])
        feedback.save_new()
        return {'msg': 'Feedback submitted'}

    @jwt_required
    def post(self):
        '''
        get a page of either resolved or unresolved feedback
        '''
        email = get_jwt_identity()
        if User.is_admin(email):
            req_json = request.get_json()
            resolved = req_json['resolved']
            page = req_json['page']
            return {
                'feedbacks': [
                    fb.to_json()
                    for fb in Feedback.get(resolved=resolved, page=page)
                ],
                'total_pages':
                Feedback.count_pages(resolved)
            }
        else:
            raise UserNotAdmin(email)

    @jwt_required
    def patch(self):
        '''
        update resolved flag on a feedback object, given by id
        NOTE: Do not simply toggle the resolved column of the object. If multiple admins are logged in going through
        feedback, a toggle could possibly result in a piece of feedback being marked incorrectly depending on
        the 'phase difference' between when their respective frontends were last updated on the backend.
        '''
        email = get_jwt_identity()
        if User.is_admin(email):
            req_json = request.get_json()
            id = req_json['id']  # specifies which feedback object to edit
            resolved = req_json[
                'resolved']  # states whether the item should be marked resolved or unresolved
            Feedback.set_resolved(id, resolved)
            return {
                'msg':
                'Feedback object {} resolved attribute set to {}'.format(
                    id, resolved),
                'total_pages':
                Feedback.count_pages(
                    not (resolved)
                )  # tell the frontend how many pages remain in !(resolved) so it can remain in sync w/ the database
            }
        else:
            raise UserNotAdmin(email)


class FullCatalog(Resource):
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

    def get(self):
        api_instance = CatalogApi()
        api_instance.api_client.configuration.access_token = SQUARE_ACCESS_TOKEN
        body = SearchCatalogObjectsRequest(
            object_types=['ITEM', 'IMAGE',
                          'CATEGORY'])  # specify all ITEM, IMAGE, and CATEGORY
        itms_imgs_and_cats = api_instance.search_catalog_objects(
            body=body
        ).objects  # List[squareconnect.models.catalog_object.CatalogObject]
        itms_only = list(
            filter(lambda obj: obj.type == 'ITEM', itms_imgs_and_cats))
        imgs_only = list(
            filter(lambda obj: obj.type == 'IMAGE', itms_imgs_and_cats))
        cats_only = list(
            filter(lambda obj: obj.type == 'CATEGORY', itms_imgs_and_cats))
        itms_w_imgs = self.__associate_item_data_with_image_data_url(
            itms_only, imgs_only)
        itms_w_imgs_w_cats = self.__associate_item_data_with_category_data(
            itms_w_imgs, cats_only)
        return {
            'msg':
            'Items retrieved',
            'items': [
                self.__catalog_item_to_dict(item.item_data)
                for item in itms_w_imgs_w_cats
            ],  # List[CatalogItem] w/ added category_data attr
            'categories': [cat.category_data.to_dict()
                           for cat in cats_only]  # List[CatalogCategory]
        }

    def __associate_item_data_with_image_data_url(self,
                                                  items: List[CatalogObject],
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
            self, items: List[CatalogObject],
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

    def __catalog_item_to_dict(self, citem: CatalogItem) -> dict:
        '''
        default to_dict function for CatalogItem doesn't capture our added category_data field, so we add it to the dictionary manually
        '''
        d = citem.to_dict()
        d['category_data'] = citem.category_data.to_dict()
        return d


# Define our callback function to check if a token has been revoked or not
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


resources_dict = {
    '/api/registration': UserRegistrationEndpoint,
    '/api/login': UserLoginEndpoint,
    '/api/account': AccountEndpoint,
    '/api/refresh': RefreshEndpoint,
    '/api/logout1': Logout1Endpoint,
    '/api/logout2': Logout2Endpoint,
    '/api/feedback': FeedbackEndpoint,
    '/api/fullcatalog': FullCatalog
}
