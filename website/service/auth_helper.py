from ..models.user import User
from typing import Dict, Tuple
from flask_restx import Namespace, fields
from typing import Dict, Tuple
from flask_bcrypt import Bcrypt  # For hashing passwords
from .. import db  # The SQLAlchemy database instance
from sqlalchemy.exc import IntegrityError
from uuid import uuid4


class Auth:
    @staticmethod
    def validate_token(name, description=None, _in="query", **kwargs):
        """
        A decorator to specify one of the expected parameters

        :param str name: the parameter name
        :param str description: a small description
        :param str _in: the parameter location `(query|header|formData|body|cookie)`
        """
        def decorator(f):
            if not hasattr(f, '__apidoc__'):
                f.__apidoc__ = {}
            if 'params' not in f.__apidoc__:
                f.__apidoc__['params'] = {}
            f.__apidoc__['params'][name] = {
                'in': _in,
                'description': description,
                **kwargs
            }
            return f
        return decorator

    @staticmethod
    def login_user(data: Dict[str, str]) -> Tuple[Dict[str, str], int]:
        try:
            # fetch the user data
            user = User.query.filter_by(email=data.get('email')).first()
            if user and user.check_password(data.get('password')):
                auth_token = User.encode_auth_token(
                    user.id)
                print(auth_token)
                if auth_token:
                    response_object = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'Authorization': auth_token
                    }
                    print(response_object)
                    return response_object, 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'email or password does not match.'
                }
                return response_object, 401

        except Exception as e:
            print(e)
            response_object = {
                'status': 'fail',
                'message': 'Try again'
            }
            return response_object, 500

    @staticmethod
    def logout_user(data: str) -> Tuple[Dict[str, str], int]:
        if data:
            auth_token = data.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                return {
                    'status': 'success',
                    'message': 'Successfully logged out.'
                }, 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': resp
                }
                return response_object, 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return response_object, 403

    @staticmethod
    def get_logged_in_user(new_request):
        # get the auth token
        auth_token = new_request.headers.get('Authorization')
        print(auth_token, "")
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                response_object = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'organization_id': user.organization_id,
                        'registered_on': str(user.registered_on)
                    }
                }
                return response_object, 200
            response_object = {
                'status': 'fail',
                'message': resp
            }
            return response_object, 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return response_object, 401

    @staticmethod
    def sign_up_user(email: str, password: str, organization_id: str = None) -> Tuple[Dict[str, str], int]:
        # Check if the user already exists
        if User.query.filter_by(email=email).first():
            return {
                'status': 'fail',
                'message': 'User already exists. Please log in.'
            }, 409

        try:
            # Create a new user instance
            new_user = User(
                email=email,
                password=password,  # This will use the setter to hash the password
                organization_id=organization_id if organization_id else uuid4()
            )

            # Add the new user to the session and commit to the database
            db.session.add(new_user)
            db.session.commit()

            # Generate the auth token
            auth_token = User.encode_auth_token(new_user.id)
            if isinstance(auth_token, bytes):
                auth_token = auth_token.decode('utf-8')

            return {
                'status': 'success',
                'message': 'Successfully registered.',
                'Authorization': auth_token
            }, 201
        except IntegrityError:
            # Rollback the session in case of an integrity error
            db.session.rollback()
            return {
                'status': 'fail',
                'message': 'Integrity error. There might be a problem with the user data.'
            }, 500
        except Exception as e:
            # Rollback the session for any other exception and return an error
            db.session.rollback()
            return {
                'status': 'fail',
                'message': f'Some error occurred. Please try again: {str(e)}'
            }, 500
