from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

ROLES = {'admin': 0, 'customer': 1}


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), unique=False)
    last_name = db.Column(db.String(64), unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    registered_on = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.Integer, nullable=False)
    square_customer_id = db.Column(db.String(64), nullable=True, unique=True)

    def __init__(self,
                 first_name: str,
                 last_name: str,
                 email: str,
                 plaintext_password: str,
                 role: int = ROLES['customer']):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = generate_password_hash(
            plaintext_password
        )  # NOTE: somebody alert the geniuses at facebook that this is how to save passwords
        self.role = role  # defaults to customer
        self.registered_on = datetime.now()

    @classmethod
    def get(cls, email: str):
        '''
        retrieve user from database by email
        '''
        return User.query.filter_by(email=email).first()

    @classmethod
    def is_admin(cls, email: str) -> bool:
        return User.get(email).role == ROLES['admin']

    def set_password(self, plaintext_password: str):
        self.password_hash = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password: str):
        return check_password_hash(self.password_hash, plaintext_password)

    def to_json(self, access_token: str, refresh_token: str) -> dict:
        '''
        Creates json (dict) of User model expected on the frontend.
        '''
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role,
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def save_new(self):
        '''
        saves new User to db
        '''
        db.session.add(self)
        db.session.commit()


class Feedback(db.Model):
    __tablename__ = 'feedback'
    rpp = 10  # results per page; NOTE: currently hardcoded, bad practice and should eventually make all pagination related vars programatic from config variable

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    email = db.Column(db.String(120), index=True)
    text = db.Column(db.Text, nullable=False)
    resolved = db.Column(db.Boolean, nullable=False)
    rcvd_on = db.Column(db.DateTime, nullable=False)

    def __init__(self,
                 name: str,
                 email: str,
                 text: str,
                 resolved: bool = False):
        self.name = name
        self.email = email
        self.text = text
        self.resolved = resolved  # default to unresolved
        self.rcvd_on = datetime.now()

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'text': self.text,
            'resolved': self.resolved,
            'rcvd_on': self.rcvd_on.isoformat()
        }

    def save_new(self):
        '''
        saves new Feedback to db
        '''
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get(cls, resolved: bool, page: int):
        '''
        gets page of resolved or unresolved Feedback objects
        '''
        return Feedback.query.filter_by(resolved=resolved).order_by(
            cls.rcvd_on).paginate(page, cls.rpp, False).items

    @classmethod
    def set_resolved(cls, id: int, resolved: bool):
        '''
        sets a Feedback object's resolved attr to value given by parameter resolved
        '''
        fb = Feedback.query.get(id)
        fb.resolved = resolved
        db.session.commit()

    @classmethod
    def count_pages(cls, resolved: bool):
        '''
        counts total number of pages in database for resolved or unresolved
        '''
        count = Feedback.query.filter_by(resolved=resolved).count()
        pages = int(count / cls.rpp)
        if (count % cls.rpp != 0):
            pages += 1
        return pages


class TokenBlacklist(db.Model):
    __tablename__ = 'token_black_list'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, index=True, nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    def save_new(self):
        '''
        saves new token to the database
        '''
        db.session.add(self)
        db.session.commit()

    def revoke(self):
        '''
        revokes token
        '''
        self.revoked = True
        db.session.commit()
