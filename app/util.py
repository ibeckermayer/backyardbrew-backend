from app import db
from flask_jwt_extended import decode_token
from datetime import datetime
from app.models import TokenBlacklist
from sqlalchemy.orm.exc import NoResultFound
from app import jwt


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
