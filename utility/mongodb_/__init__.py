from .model import MongodbAction
from .globals import mongodb_manager

def initialize(app, echo: bool = False):
    """Initialize MONGO with application."""

    # get application config.
    host = app.config['MONGO_DATABASE_URI']
    testing = app.config["TESTING"]
    db_name = app.config['MONGO_DATABASE_NAME']
    collection = app.config['MONGO_DATABASE_COLLECTION']
    mongodb_manager.setup_host(host, testing, db_name, collection)
    
    
def setup(host: str, testing: bool, db_name: str, collection: str):
    mongodb_manager.setup_host(host, testing, db_name, collection)