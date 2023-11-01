from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_restx import Api
from .config import Config

# Initialize Flask extensions
db = SQLAlchemy()
flask_bcrypt = Bcrypt()


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    flask_bcrypt.init_app(app)
    db.init_app(app)

    # Import models
    from .models.user import User  # Make sure to import the User model

    with app.app_context():
        # Create tables for our models
        db.create_all()

        # Initialize Flask-Restx Api
        api = Api(app, title='My API', version='1.0',
                  description='A description')

        # Import and register the namespaces for your resources here
        from .controllers.auth import api as auth_ns
        from .controllers.user import api as user_ns
        api.add_namespace(auth_ns, path='/auth')
        api.add_namespace(user_ns, path='/user')

        return app
