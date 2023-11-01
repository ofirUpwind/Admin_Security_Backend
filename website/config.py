import os

key = "MyJwtLovelyKey1234567890!!1234567890"
# create a config class for the Postgres connection


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Ykpui9753$@localhost:5432/master'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
