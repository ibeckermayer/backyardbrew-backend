import os
from dateutil import relativedelta


class Config(object):
    """Parent configuration class."""
    # DEBUG = True
    SECRET_KEY = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = "127.0.0.1:5000"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/backyardbrew_dev_db'


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/backyardbrew_test_db'
    DEBUG = True


def JwtAccessImmediateExpireConfig(parent: Config):
    '''pass which configuration you wish to inherit in the parent parameter. This allows devs to choose whether to play with immediate jwt access token expiration on either the development server/database with DevelopmentConfig, or use it in testing with the TestingConfig'''

    class JwtAccessImmediateExpireConfig(parent):
        JWT_ACCESS_TOKEN_EXPIRES = relativedelta.relativedelta(
            microseconds=1)  # access token expires in 1 microsecond (minimum)

    return JwtAccessImmediateExpireConfig()


def JwtRefreshImmediateExpireConfig(parent: Config):
    '''similar principle to JwtAccessImmediateExpireConfig, see it's docstring'''

    class JwtRefreshImmediateExpireConfig(parent):
        JWT_REFRESH_TOKEN_EXPIRES = relativedelta.relativedelta(
            microseconds=1)  # refresh token expires in 1 microsecond (minimum)

    return JwtRefreshImmediateExpireConfig()


class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False


app_config = {
    'development':
    DevelopmentConfig,
    'testing':
    TestingConfig,
    'staging':
    StagingConfig,
    'production':
    ProductionConfig,
    'jwt_access_immediate_expire_dev':
    JwtAccessImmediateExpireConfig(DevelopmentConfig),
    'jwt_access_immediate_expire_test':
    JwtAccessImmediateExpireConfig(TestingConfig),
    'jwt_refresh_immediate_expire_dev':
    JwtRefreshImmediateExpireConfig(DevelopmentConfig),
    'jwt_refresh_immediate_expire_test':
    JwtRefreshImmediateExpireConfig(TestingConfig)
}
