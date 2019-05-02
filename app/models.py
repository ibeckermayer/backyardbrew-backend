from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

ROLES = {'admin': 0, 'customer': 1}


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=False)
    last_name = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    registered_on = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.Integer, nullable=False)

    def __init__(self, first_name: str, last_name: str, email: str,
                 plaintext_password: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = generate_password_hash(plaintext_password)
        self.registered_on = datetime.now()
        self.role = ROLES['customer']

    def set_password(self, plaintext_password: str):
        self.password_hash = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password: str):
        return check_password_hash(self.password_hash, plaintext_password)

    def to_json(self) -> dict:
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role
        }


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True)
    text = db.Column(db.Text, nullable=False)
    resolved = db.Column(db.Boolean, nullable=False)
    rcvd_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, email: str, text: str):
        self.email = email
        self.text = text
        self.resolved = False  # new Feedback objects are always unresolved
        self.rcvd_on = datetime.now()

    def to_json(self) -> dict:
        return {
            'email': self.email,
            'text': self.text,
            'resolved': self.resolved,
            'rcvd_on': self.rcvd_on
        }


class TokenBlacklist(db.Model):
    __tablename__ = 'token_black_list'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
