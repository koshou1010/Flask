from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager


class User(Base):
    __tablename__ = "user"
    id = Column(types.Integer, primary_key=True, autoincrement=True)
    create_time = Column(types.BigInteger, nullable=False)
    uuid = Column(types.Integer, nullable=False, unique=True)
    name = Column(types.String(255), nullable=False)
    sex = Column(types.String(255), nullable=False)
    age = Column(types.Integer, nullable=True)
    birthday = Column(types.String(255), nullable=True)
    height = Column(types.Integer, nullable=True)
    weight = Column(types.Integer, nullable=True)
    line_id = Column(types.String(255), nullable=True)