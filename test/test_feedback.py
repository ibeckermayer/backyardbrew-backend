from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from time import sleep
from dateutil import relativedelta
import requests
import json
import lorem
from backend import (test_feedback_unresolved, test_feedback_resolved,
                     add_test_feedback, test_users, add_test_user,
                     add_all_test_feedback)
from app.models import Feedback

ENDPOINT = '/api/feedback'


def test_put_feedback(testing_client: FlaskClient, testing_db: SQLAlchemy):
    '''
    test feedback is submitted and saved successfully to the database
    '''
    test_fb = test_feedback_unresolved[0]

    response = testing_client.put(ENDPOINT,
                                  data=json.dumps({
                                      'name': test_fb['name'],
                                      'email': test_fb['email'],
                                      'text': test_fb['text']
                                  }),
                                  content_type='application/json')

    status_code = response.status_code
    response_json = json.loads(response.data)

    assert status_code == 200
    assert response_json['msg'] == 'Feedback submitted'

    # check that feedback object has indeed been saved to db
    db_fb_objs = Feedback.get(False, 1)
    db_fb_obj = db_fb_objs[0]
    assert len(db_fb_objs) == 1
    assert db_fb_obj.id == 1
    assert db_fb_obj.name == test_fb['name']
    assert db_fb_obj.email == test_fb['email']
    assert db_fb_obj.text == test_fb['text']
    assert db_fb_obj.resolved == False


def test_post_feedback_no_jwt(testing_client: FlaskClient,
                              testing_db: SQLAlchemy):
    '''
    ensure post endpoint is protected by jwt
    '''
    # add single object of resolved feedback to database and a single unresolved feedback
    test_fb_r = test_feedback_resolved[0]
    add_test_feedback(test_fb_r)
    test_fb_u = test_feedback_unresolved[0]
    add_test_feedback(test_fb_u)

    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': True,
            'page': 1,
        }),
        content_type='application/json',
    )

    response_json = json.loads(response.data)

    assert response.status_code == 401
    assert response_json['msg'] == 'Missing Authorization Header'


def test_post_feedback_jwt_expired(testing_client: FlaskClient,
                                   testing_db: SQLAlchemy):
    '''
    try to post feedback with expired jwt
    '''
    # set access_token to expire quickly
    testing_client.application.config[
        'JWT_ACCESS_TOKEN_EXPIRES'] = relativedelta.relativedelta(
            microseconds=1)  # access token expires in 1 microsecond (minimum)

    # add single object of resolved feedback to database and a single unresolved feedback
    test_fb_r = test_feedback_resolved[0]
    add_test_feedback(test_fb_r)
    test_fb_u = test_feedback_unresolved[0]
    add_test_feedback(test_fb_u)

    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')
    sleep(1.1)  # sleep for 1.1 second to allow access_token to expire
    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': True,
            'page': 1,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    assert response.status_code == 401
    assert response_json['msg'] == 'Token has expired'


def test_post_feedback_unauthorized_user(testing_client: FlaskClient,
                                         testing_db: SQLAlchemy):
    '''
    try to post feedback as non-admin user
    '''
    # add single object of resolved feedback to database and a single unresolved feedback
    test_fb_r = test_feedback_resolved[0]
    add_test_feedback(test_fb_r)
    test_fb_u = test_feedback_unresolved[0]
    add_test_feedback(test_fb_u)

    # add customer user to db
    test_customer = test_users['test_customer']
    add_test_user(test_customer)

    # login as customer
    login_response = testing_client.post(
        '/api/login',
        data=json.dumps({
            'email':
            test_customer['email'],
            'plaintext_password':
            test_customer['plaintext_password']
        }),
        content_type='application/json')
    # login should succeed
    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    # try to access endpoint
    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': True,
            'page': 1,
        }),
        content_type='application/json',
        headers=access_header,
    )
    response_json = json.loads(response.data)

    # should say this user is unauthorized
    assert response.status_code == 403
    assert response_json[
        'msg'] == 'User {} does not have admin privileges'.format(
            test_customer['email'])


def test_post_feedback_no_feedback(testing_client: FlaskClient,
                                   testing_db: SQLAlchemy):
    '''
    try postting feedback (both resolved and unresolved) with no feedback in the database and ensure
    zero pages are calculated and empty list of feedbacks is returned
    '''
    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': True,
            'page': 1,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(response_json['feedbacks']) == 0
    assert response_json['total_pages'] == 0

    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': False,
            'page': 1,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert len(response_json['feedbacks']) == 0
    assert response_json['total_pages'] == 0


def test_post_feedback_resolved(testing_client: FlaskClient,
                                testing_db: SQLAlchemy):
    '''
    post single resolved feedback with no pagination
    '''
    # add single object of resolved feedback to database and a single unresolved feedback
    test_fb_r = test_feedback_resolved[0]
    add_test_feedback(test_fb_r)
    test_fb_u = test_feedback_unresolved[0]
    add_test_feedback(test_fb_u)

    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': True,
            'page': 1,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert response_json['total_pages'] == 1
    assert len(response_json['feedbacks']) == 1
    assert response_json['feedbacks'][0]['id'] == 1
    assert response_json['feedbacks'][0]['name'] == test_fb_r['name']
    assert response_json['feedbacks'][0]['email'] == test_fb_r['email']
    assert response_json['feedbacks'][0]['text'] == test_fb_r['text']
    assert response_json['feedbacks'][0]['resolved'] == True


def test_post_feedback_unresolved(testing_client: FlaskClient,
                                  testing_db: SQLAlchemy):
    '''
    post single unresolved feedback with no pagination
    '''
    # add single object of resolved feedback to database and a single unresolved feedback
    test_fb_r = test_feedback_resolved[0]
    add_test_feedback(test_fb_r)
    test_fb_u = test_feedback_unresolved[0]
    add_test_feedback(test_fb_u)

    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': False,
            'page': 1,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    assert response.status_code == 200
    assert response_json['total_pages'] == 1
    assert len(response_json['feedbacks']) == 1
    assert response_json['feedbacks'][0]['id'] == 2
    assert response_json['feedbacks'][0]['name'] == test_fb_u['name']
    assert response_json['feedbacks'][0]['email'] == test_fb_u['email']
    assert response_json['feedbacks'][0]['text'] == test_fb_u['text']
    assert response_json['feedbacks'][0]['resolved'] == False


def test_post_feedback_resolved_pag(testing_client: FlaskClient,
                                    testing_db: SQLAlchemy):
    '''
    Test more complex queries for resolved feedback that include pagination, with all 15 resolved and unresolved in the database
    '''
    # add all the test_feedback from backend.py to database
    add_all_test_feedback()

    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    # check page 1
    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': True,
            'page': 1,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    feedbacks = response_json['feedbacks']
    assert response_json['total_pages'] == 2
    assert response.status_code == 200
    assert len(
        feedbacks
    ) == 10  # NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable
    for feedback in feedbacks:
        assert feedback['resolved'] == True

    # check page 2
    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': True,
            'page': 2,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    feedbacks = response_json['feedbacks']
    assert response.status_code == 200
    assert response_json['total_pages'] == 2
    assert len(
        feedbacks
    ) == 5  # NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable
    for feedback in feedbacks:
        assert feedback['resolved'] == True


def test_post_feedback_unresolved_pag(testing_client: FlaskClient,
                                      testing_db: SQLAlchemy):
    '''
    Test more complex queries for unresolved feedback that include pagination, with all 15 resolved and unresolved in the database
    '''
    # add all the test_feedback from backend.py to database
    add_all_test_feedback()

    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    # check page 1
    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': False,
            'page': 1,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    feedbacks = response_json['feedbacks']
    assert response_json['total_pages'] == 2
    assert response.status_code == 200
    assert len(
        feedbacks
    ) == 10  # NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable
    for feedback in feedbacks:
        assert feedback['resolved'] == False

    # check page 2
    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': False,
            'page': 2,
        }),
        content_type='application/json',
        headers=access_header,
    )

    response_json = json.loads(response.data)
    feedbacks = response_json['feedbacks']
    assert response_json['total_pages'] == 2
    assert response.status_code == 200
    assert len(
        feedbacks
    ) == 5  # NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable
    for feedback in feedbacks:
        assert feedback['resolved'] == False


def test_patch_feedback_no_jwt(testing_client: FlaskClient,
                               testing_db: SQLAlchemy):
    '''
    Test patch feedback without jwt header
    '''
    # add all the test_feedback from backend.py to database
    add_all_test_feedback()

    response = testing_client.patch(
        ENDPOINT,
        data=json.dumps({
            'id': 1,  # hardcoded id 1
            'resolved': True,
        }),
        content_type='application/json')
    response_json = json.loads(response.data)

    assert response.status_code == 401
    assert response_json['msg'] == 'Missing Authorization Header'


def test_patch_feedback_jwt_expired(testing_client: FlaskClient,
                                    testing_db: SQLAlchemy):
    '''
    test patch feedback with expired jwt
    '''
    # set access_token to expire quickly
    testing_client.application.config[
        'JWT_ACCESS_TOKEN_EXPIRES'] = relativedelta.relativedelta(
            microseconds=1)  # access token expires in 1 microsecond (minimum)

    # add all the test_feedback from backend.py to database
    add_all_test_feedback()

    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)
    sleep(1.1)  # sleep for 1.1 second to allow access_token to expire

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.patch(
        ENDPOINT,
        data=json.dumps({
            'id': 1,  # hardcoded row 1
            'resolved': False
        }),
        content_type='application/json',
        headers=access_header)

    response_json = json.loads(response.data)
    assert response.status_code == 401
    assert response_json['msg'] == 'Token has expired'


def test_patch_feedback_unauthorized_user(testing_client: FlaskClient,
                                          testing_db: SQLAlchemy):
    '''
    test patch feedback with non-admin user
    '''
    # add all the test_feedback from backend.py to database
    add_all_test_feedback()

    # add customer user to db
    test_customer = test_users['test_customer']
    add_test_user(test_customer)

    # login as customer
    login_response = testing_client.post(
        '/api/login',
        data=json.dumps({
            'email':
            test_customer['email'],
            'plaintext_password':
            test_customer['plaintext_password']
        }),
        content_type='application/json')
    # login should succeed
    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.patch(
        ENDPOINT,
        data=json.dumps({
            'id': 1,  # hardcoded row 1
            'resolved': False
        }),
        content_type='application/json',
        headers=access_header)

    response_json = json.loads(response.data)

    # should say this user is unauthorized
    assert response.status_code == 403
    assert response_json[
        'msg'] == 'User {} does not have admin privileges'.format(
            test_customer['email'])


def test_patch_feedback_res_to_un(testing_client: FlaskClient,
                                  testing_db: SQLAlchemy):
    '''
    Test changing a resolved feedback object to unresolved
    '''
    # add all the test_feedback from backend.py to database
    add_all_test_feedback()

    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    # post page 2
    response = testing_client.post(ENDPOINT,
                                   data=json.dumps({
                                       'resolved': True,
                                       'page': 2,
                                   }),
                                   content_type='application/json',
                                   headers=access_header)

    response_json = json.loads(response.data)
    feedbacks = response_json['feedbacks']
    assert response.status_code == 200
    assert response_json['total_pages'] == 2
    assert len(
        feedbacks
    ) == 5  # NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable

    # extract feedback object to change
    fb = feedbacks[0]
    id = fb['id']

    # edit feedback object
    response = testing_client.patch(ENDPOINT,
                                    data=json.dumps({
                                        'id': id,
                                        'resolved': False
                                    }),
                                    content_type='application/json',
                                    headers=access_header)

    assert (json.loads(response.data))['total_pages'] == 2

    # check page 2 again, this time there should only be 4 feedbacks
    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': True,
            'page': 2,
        }),
        content_type='application/json',
        headers=access_header,
    )
    response_json = json.loads(response.data)
    feedbacks = response_json['feedbacks']
    assert response.status_code == 200
    assert response_json['total_pages'] == 2
    assert len(
        feedbacks
    ) == 4  # NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable


def test_patch_feedback_un_to_res(testing_client: FlaskClient,
                                  testing_db: SQLAlchemy):
    '''
    Test changing a unresolved feedback object to resolved
    '''
    # add all the test_feedback from backend.py to database
    add_all_test_feedback()

    # add admin user to db
    test_admin = test_users['test_admin']
    add_test_user(test_admin)

    # login as admin
    login_response = testing_client.post('/api/login',
                                         data=json.dumps({
                                             'email':
                                             test_admin['email'],
                                             'plaintext_password':
                                             test_admin['plaintext_password']
                                         }),
                                         content_type='application/json')

    login_response_json = json.loads(login_response.data)

    # create access header
    access_token = login_response_json['user']['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    # post page 2
    response = testing_client.post(ENDPOINT,
                                   data=json.dumps({
                                       'resolved': False,
                                       'page': 2,
                                   }),
                                   content_type='application/json',
                                   headers=access_header)

    response_json = json.loads(response.data)
    feedbacks = response_json['feedbacks']
    assert response.status_code == 200
    assert response_json['total_pages'] == 2
    assert len(
        feedbacks
    ) == 5  # NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable

    # extract feedback object to change
    fb = feedbacks[0]
    id = fb['id']

    # edit feedback object
    response = testing_client.patch(ENDPOINT,
                                    data=json.dumps({
                                        'id': id,
                                        'resolved': True
                                    }),
                                    content_type='application/json',
                                    headers=access_header)

    assert (json.loads(response.data))['total_pages'] == 2

    # check page 2 again, this time there should only be 4 feedbacks
    response = testing_client.post(
        ENDPOINT,
        data=json.dumps({
            'resolved': False,
            'page': 2,
        }),
        content_type='application/json',
        headers=access_header,
    )
    response_json = json.loads(response.data)
    feedbacks = response_json['feedbacks']
    assert response.status_code == 200
    assert response_json['total_pages'] == 2
    assert len(
        feedbacks
    ) == 4  # NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable
