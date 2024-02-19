from dotenv import load_dotenv
import os
from os import urandom
from datetime import timedelta

load_dotenv("./config/.env")

class Config:
    ENV = 'default'
    DEBUG = False
    TESTING = False

    # Secret Key Config.
    SECRET_KEY = urandom(24)

    # Json Web Token Config.
    JWT_SECRET_KEY = urandom(24)
    JWT_ALGORITHM = 'HS256'
    JWT_DECODE_ALGORITHMS = 'HS256'
    JWT_TOKEN_LOCATION = 'headers'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=15)
    JWT_CLAIMS_IN_REFRESH_TOKEN = False

    # SQL Alchemy Config.
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # MongoDB Config.
    MONGO_DATABASE_URI = ''

    # Cross-Origin Resource Sharing Config.
    CORS_ALLOWED_ORIGINS = '*'

    # WebSocket Config.
    WEBSOCKET_CORS_ALLOWED_ORIGINS = '*'
    WEBSOCKET_ASYNC_MODE = 'eventlet'
    WEBSOCKET_PING_INTERVAL = 5000
    WEBSOCKET_PING_TIMEOUT = 60000

    @staticmethod
    def init_app(app):
        pass


class LocalConfig(Config):
    ENV = os.getenv('MODE')
    DEBUG = True
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
        app.config['MONGO_DATABASE_URI'] = os.getenv('MONGO_DATABASE_URI')
        app.config['MONGO_DATABASE_NAME']  = os.getenv('MONGO_DATABASE_NAME')
        app.config['MONGO_DATABASE_COLLECTION'] = os.getenv('MONGO_DATABASE_COLLECTION')
        app.config['LINE_CHANNEL_ACCESS_TOKEN'] = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        app.config['LINE_CHANNEL_SECRET'] = os.getenv('LINE_CHANNEL_SECRET')
        
        # Model Initialize.
        from utility.sql_alchemy import initialize
        initialize(app)
        
        # Mongodb Initialize
        from utility.mongodb_ import initialize
        initialize(app)
         
        # Initialize WebSocket.
        from utility.websocket import initialize
        initialize(app)
        
        # Logger Initialize.
        from utility.logger import initialize
        initialize(app)

class TestingConfig(Config):
    ENV = 'testing'
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    # Cross-Origin Resource Sharing Config.
    CORS_ALLOWED_ORIGINS = '*'


    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        import json
        mode = 'test'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:{}/{}'.format('test_user', 'tester', 'localhost', '8080', 'test')
        app.config['MONGO_DATABASE_URI']  =  'mongodb://{}:{}@{}:{}/?authMechanism=DEFAULT'.format('supercharge', 'secret', 'localhost', '27017')
        app.config['MONGO_DATABASE_NAME']  = 'supercharge'
        app.config['MONGO_DATABASE_COLLECTION']  = 'seven_days_history'
        
        # Model Initialize.
        from utility.sql_alchemy import initialize
        initialize(app)
        
        # Mongodb Initialize
        from utility.mongodb_ import initialize
        initialize(app)
         
        # Initialize WebSocket.
        from utility.websocket import initialize
        initialize(app)

        # Logger Initialize.
        from utility.logger import initialize
        initialize(app)

class DevelopConfig(Config):
    ENV = os.getenv('MODE')
    DEBUG = True
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
        app.config['MONGO_DATABASE_URI'] = os.getenv('MONGO_DATABASE_URI')
        app.config['MONGO_DATABASE_NAME']  = os.getenv('MONGO_DATABASE_NAME')
        app.config['MONGO_DATABASE_COLLECTION'] = os.getenv('MONGO_DATABASE_COLLECTION')

        
        # Model Initialize.
        from utility.sql_alchemy import initialize
        initialize(app)
        
        # Mongodb Initialize
        from utility.mongodb_ import initialize
        initialize(app)
         
        # Initialize WebSocket.
        from utility.websocket import initialize
        initialize(app)

        # Logger Initialize.
        from utility.logger import initialize
        initialize(app)
        
class ReleaseConfig(Config):
    ENV = os.getenv('MODE')
    DEBUG = True
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
        app.config['MONGO_DATABASE_URI'] = os.getenv('MONGO_DATABASE_URI')
        app.config['MONGO_DATABASE_NAME']  = os.getenv('MONGO_DATABASE_NAME')
        app.config['MONGO_DATABASE_COLLECTION'] = os.getenv('MONGO_DATABASE_COLLECTION')

        
        # Model Initialize.
        from utility.sql_alchemy import initialize
        initialize(app)
        
        # Mongodb Initialize
        from utility.mongodb_ import initialize
        initialize(app)
         
        # Initialize WebSocket.
        from utility.websocket import initialize
        initialize(app)

        # Logger Initialize.
        from utility.logger import initialize
        initialize(app)




config = {
    'main': LocalConfig,
    'test' : TestingConfig,
    'develop' : DevelopConfig,
    'release' : ReleaseConfig
}
