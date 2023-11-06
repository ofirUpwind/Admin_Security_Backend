import os
from sqlalchemy import create_engine

# Your secret key for JWT encoding/decoding
key = "MyJwtLovelyKey1234567890!!1234567890"


class Config(object):
    # Your PostgreSQL database URI
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Ykpui9753$@mypostgresdb.cq5n0l48wnd0.us-east-1.rds.amazonaws.com:5432/master'
    # Set to False to disable the tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Create the SQLAlchemy engine instance
    # You can add the echo=True parameter if you want to log all the statements executed by SQLAlchemy
    ENGINE = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
