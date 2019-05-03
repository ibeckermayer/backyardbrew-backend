from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from time import sleep
from dateutil import relativedelta
import requests
import json
import lorem
from backend import (test_feedback_unresolved, test_feedback_resolved,
                     add_test_feedback, test_users, add_test_user)

ENDPOINT = '/api/feedback'


def test_submit_feedback(testing_client: FlaskClient, testing_db: SQLAlchemy):
    '''
    test feedback is submitted successfully
    '''
    test_fb = test_feedback_unresolved[0]

    response = testing_client.post(ENDPOINT,
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


def test_get_feedback_no_jwt(testing_client: FlaskClient,
                             testing_db: SQLAlchemy):
    '''
    ensure endpoint is protected by jwt
    '''
    # add single object of resolved feedback to database and a single unresolved feedback
    test_fb_r = test_feedback_resolved[0]
    add_test_feedback(test_fb_r)
    test_fb_u = test_feedback_unresolved[0]
    add_test_feedback(test_fb_u)

    response = testing_client.get(
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


def test_get_feedback_jwt_expired(testing_client: FlaskClient,
                                  testing_db: SQLAlchemy):
    '''
    get single resolved feedback with no pagination
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
    access_token = login_response_json['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.get(
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


def test_get_feedback_unauthorized_user(testing_client: FlaskClient,
                                        testing_db: SQLAlchemy):
    '''
    attempt to access endpoint as customer
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
    access_token = login_response_json['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    # try to access endpoint
    response = testing_client.get(
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


def test_get_feedback_no_feedback(testing_client: FlaskClient,
                                  testing_db: SQLAlchemy):
    '''
    try getting feedback (both resolved and unresolved) with no feedback in the database and ensure
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
    access_token = login_response_json['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.get(
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
    assert response_json['total_pages'] == 0
    assert len(response_json['feedbacks']) == 0

    response = testing_client.get(
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
    assert response_json['total_pages'] == 0
    assert len(response_json['feedbacks']) == 0


def test_get_feedback_resolved(testing_client: FlaskClient,
                               testing_db: SQLAlchemy):
    '''
    get single resolved feedback with no pagination
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
    access_token = login_response_json['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.get(
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


def test_get_feedback_unresolved(testing_client: FlaskClient,
                                 testing_db: SQLAlchemy):
    '''
    get single unresolved feedback with no pagination
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
    access_token = login_response_json['access_token']
    access_header = {'Authorization': 'Bearer ' + access_token}

    response = testing_client.get(
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
