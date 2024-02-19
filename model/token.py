from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager
import datetime as dt

class Token(BaseModel, Base):
    __tablename__ = "token"
    id = Column(types.Integer, primary_key=True, autoincrement=True)
    token = Column(types.String(255), nullable=False, unique=True)
    customer = Column(types.String(55), nullable=False, unique=True)
    create_time = Column(types.Integer)
    permission = Column(types.String(55))
    expire_datetime = Column(types.DateTime)


