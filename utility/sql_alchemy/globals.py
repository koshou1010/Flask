from sqlalchemy.ext.declarative import declarative_base
from .model import SQLAlchemy_Manager


Base = declarative_base()
sqlAlchemy_manager = SQLAlchemy_Manager()
