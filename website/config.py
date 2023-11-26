import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()


class Config(object):

    # Fetch the local and production database URIs from environment variables
    SQLALCHEMY_DATABASE_URI_LOCAL = os.environ.get('DATABASE_URI_LOCAL')
    SQLALCHEMY_DATABASE_URI_PROD = os.environ.get('DATABASE_URI_PROD')

    # Determine which URI to use
    if os.getenv('IS_LOCALHOST') == 'false':
        # Use the production database URI if not localhost
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_PROD
    else:
        # Use the local database URI otherwise
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_LOCAL

    # Create the SQLAlchemy engine instance
    ENGINE = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)


# Your secret key for JWT encoding/decoding
key = os.environ.get('JWT_SECRET_KEY')
