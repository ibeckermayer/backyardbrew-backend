from flask_restful import Resource, request
from sqlalchemy.exc import IntegrityError
from app.models import User, Feedback
from app import db, jwt
from app.errors import EmailAlreadyInUse, UserDNE, PasswordIncorrect, UserNotAdmin
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt, jwt_optional)
from app.util import (add_token_to_database, is_token_revoked, revoke_token,
                      square_get_full_catalog, square_get_checkout_url,
                      square_create_user)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os


class UserRegistrationEndpoint(Resource):

  def put(self):
    user_json = request.get_json()
    if User.get(user_json['email']) is not None:
      raise EmailAlreadyInUse()
    user = User(
        first_name=user_json['first_name'],
        last_name=user_json['last_name'],
        email=user_json['email'],
        plaintext_password=user_json['plaintext_password'])
    square_customer_id = square_create_user(
        given_name=user.first_name,
        family_name=user.last_name,
        email_address=user.email,
        reference_id=user.id)
    user.square_customer_id = square_customer_id
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
    submit new piece of feedback and send an email to customer service email
    '''
    feedback_json = request.get_json()
    name = feedback_json['name']
    email = feedback_json['email']
    text = feedback_json['text']

    feedback = Feedback(name=name, email=email, text=text)
    feedback.save_new()

    message = Mail(
        from_email='ibeckermayer@gmail.com',
        to_emails='ibeckermayer@gmail.com',
        subject='New support ticket from {}'.format(name),
        html_content='<div>{}</div><div>reply to: {}</div>'.format(text, email))
    try:
      sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
      response = sg.send(message)
      print(response.status_code)
      print(response.body)
      print(response.headers)
    except Exception as e:
      print(e.message)

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
              fb.to_json() for fb in Feedback.get(resolved=resolved, page=page)
          ],
          'total_pages': Feedback.count_pages(resolved)
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
  see docstring for square_get_full_catalog() for details
  '''

  def get(self):
    return square_get_full_catalog()


class GenerateCheckoutUrl(Resource):
  '''
  accepts a cart and returns a checkout url for that cart
  TODO: make jwt_optional to attribute order with user_id (get_jwt_identity, associate id, put that in request to square for later search)
  '''

  @jwt_optional
  def post(self):
    square_customer_id = None
    email = get_jwt_identity()
    if (email):
      user = User.get(email)
      square_customer_id = user.square_customer_id

    req_json = request.get_json()
    cart = req_json
    return square_get_checkout_url(cart, square_customer_id)


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
    '/api/fullcatalog': FullCatalog,
    '/api/generate_checkout_url': GenerateCheckoutUrl
}
