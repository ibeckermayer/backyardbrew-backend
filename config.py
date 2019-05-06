import os
from dateutil import relativedelta


class Config(object):
    """Parent configuration class."""
    # DEBUG = True
    SECRET_KEY = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SERVER_NAME = "127.0.0.1:5000"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/backyardbrew_dev_db'  # uncomment for OSX
    # SQLALCHEMY_DATABASE_URI = 'postgresql:///backyardbrew_dev_db'  # uncomment for Ubuntu
    SECRET_KEY = 'my-super-secret-key'


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/backyardbrew_test_db'  # uncomment for OSX
    # SQLALCHEMY_DATABASE_URI = 'postgresql:///backyardbrew_test_db'  # uncomment for Ubuntu
    DEBUG = True


class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}

SQUARE_ACCESS_TOKEN = os.getenv('SQUARE_ACCESS_TOKEN')
