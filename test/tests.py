from flask_testing import TestCase
from app import create_app, db
from config import TestConfig


class BaseTest(TestCase):
    def create_app(self):
        return create_app(self, TestConfig)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
