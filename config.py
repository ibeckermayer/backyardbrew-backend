import os
from dateutil import relativedelta


class Config(object):
    """Parent configuration class."""
    SECRET_KEY = os.urandom(12).hex()
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/backyardbrew_dev_db'  # uncomment for OSX
    # SQLALCHEMY_DATABASE_URI = 'postgresql:///backyardbrew_dev_db'  # uncomment for Ubuntu


class ImmediateJwtExpireConfig(Config):
    """Configurations for Manually testing immediate jwt expiration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/backyardbrew_dev_db'  # uncomment for OSX
    # SQLALCHEMY_DATABASE_URI = 'postgresql:///backyardbrew_dev_db'  # uncomment for Ubuntu
    JWT_ACCESS_TOKEN_EXPIRES = relativedelta.relativedelta(
        microseconds=1)  # access token expires in 1 microsecond (minimum)
    JWT_REFRESH_TOKEN_EXPIRES = relativedelta.relativedelta(
        microseconds=1)  # refresh token expires in 1 microsecond (minimum)


class ThreeSecJwtAccessExpireConfig(Config):
    """Configurations for manually testing jwt access expiring (quickly)"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/backyardbrew_dev_db'  # uncomment for OSX
    # SQLALCHEMY_DATABASE_URI = 'postgresql:///backyardbrew_dev_db'  # uncomment for Ubuntu
    JWT_ACCESS_TOKEN_EXPIRES = relativedelta.relativedelta(
        seconds=3)  # access token expires in 1 microsecond (minimum)


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/backyardbrew_test_db'  # uncomment for OSX
    # SQLALCHEMY_DATABASE_URI = 'postgresql:///backyardbrew_test_db'  # uncomment for Ubuntu


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
    'production': ProductionConfig,
    'immediatejwtexpire': ImmediateJwtExpireConfig,
    'threesecjwtexpire': ThreeSecJwtAccessExpireConfig
}

SQUARE_ACCESS_TOKEN = os.getenv('SQUARE_ACCESS_TOKEN')
SQUARE_LOCATION_ID = os.getenv('SQUARE_LOCATION_ID')
