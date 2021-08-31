import os
basedir = os.path.abspath(os.path.dirname(__file__))
import boto3
import json
import utils 

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS= False
    SQLALCHEMY_DATABASE_URI = utils._get_db_string()

class DevelopmentConfig(Config):
    """
    """
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    

class ProductionConfig(Config):
    SECRET_KEY = 'THIS NEEDS A VALUE'
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = 'THIS NEEDS A VALUE'
