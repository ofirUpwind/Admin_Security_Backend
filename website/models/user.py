# models.py

from .. import db
import datetime
from uuid import uuid4
import jwt
from typing import Union, Optional
from ..config import key
import flask_bcrypt
from flask_restx import Namespace, fields


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    registered_on = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.now)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    organization_id = db.Column(db.String(100), nullable=True, default=uuid4())
    public_id = db.Column(db.String(100), unique=True,
                          default=lambda: str(uuid4()))
    password_hash = db.Column(db.String(100))

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def encode_auth_token(user_id: int) -> bytes:
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                key,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token: str, return_preference: Optional[str] = None) -> Union[str, int]:
        try:
            payload = jwt.decode(auth_token, key, algorithms=['HS256'])
            # This should be replaced with actual check if using token blacklist
            is_blacklisted_token = False
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub'] if return_preference is None else payload[return_preference]
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    def __repr__(self):
        return f"<User '{self.email}'>"


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'email': fields.String(required=True, description='user email address'),
        'public_id': fields.String(description='user Identifier')
    })

    user_out = api.inherit('user_out', user, {
        'organization_id': fields.String(description='organization identifier')
    })


class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password'),
    })
