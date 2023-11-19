from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restx import Api
from website.config import Config
import json
import datetime


# Initialize Flask extensions
db = SQLAlchemy()
flask_bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    flask_bcrypt.init_app(app)
    db.init_app(app)

    # Import models here to avoid circular imports
    # This needs to be after db is initialized and within the context
    from .models.user import User
    from .models.audit import Audit

    with app.app_context():
        # Create tables for our models
        db.create_all()

        # Initialize Flask-Restx Api
        api = Api(app, title='My API', version='1.0',
                  description='A description')

        # Import and register namespaces within the context
        from .controllers.auth import api as auth_ns
        from .controllers.user import api as user_ns
        from .controllers.user import api1 as query_ns
        api.add_namespace(auth_ns, path='/auth')
        api.add_namespace(user_ns, path='/user')
        api.add_namespace(query_ns, path='/query')

        # Before request hook
        @app.before_request
        def before_request_func():
            g.request_start_time = datetime.datetime.now()

    # Skip token decoding for login and signup routes
            if '/login' not in request.path and '/sign-up' not in request.path:
                token = request.headers.get('Authorization')

                if token:
                    # Assuming the token is a Bearer token
                    decoded_token = User.decode_auth_token(token)
                    if isinstance(decoded_token, dict) and 'public_id' in decoded_token:
                        g.user_public_id = decoded_token['public_id']
                        print(g.user_public_id, "g.user_public_id")
                else:
                    # Handle error or set to None if the public_id is not in the token
                    g.user_public_id = None

            # Check if the return value is an integer, which will be the user ID
                    # The returned value is an error message string, handle accordingly
                    # Her

        # After request hook

        @app.after_request
        def after_request_func(response):

            # This is where you'd access the request and response objects
            # and potentially use them for logging, auditing, etc.
            # Assuming you have the log_audit_entry function properly defined elsewhere
            # Use the time captured in before_request_func or default to now if not set
            request_start_time = g.get(
                'request_start_time', datetime.datetime.now())

            # Here's an example of capturing request and response details:
            status_code = response.status_code
            request_origin = 'API' if 'application/json' in request.headers.get(
                'Content-Type', '') else 'UI'
            user_public_id = g.get('user_public_id', '')
            route = request.path
            body = request.get_json() if request.is_json else None

            # Call the log_audit_entry function from your audit service
            from .service.audit_service import log_audit_entry
            log_audit_entry(
                status_code=status_code,
                request_origin=request_origin,
                user_public_id=user_public_id,
                route=route,
                body=body,
                request_start_time=request_start_time
            )

            return response

        return app
