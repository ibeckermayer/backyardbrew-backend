from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=False)
    last_name = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    authenticated = db.Column(db.Boolean, default=False)
    registered_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, first_name: str, last_name: str, email: str,
                 plaintext_password: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = generate_password_hash(plaintext_password)
        self.authenticated = False
        self.registered_on = datetime.now()

    def set_password(self, plaintext_password: str):
        self.password_hash = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password: str):
        return check_password_hash(self.password_hash, plaintext_password)

    def to_json(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email
        }


class TokenBlacklist(db.Model):
    __tablename__ = 'token_black_list'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
