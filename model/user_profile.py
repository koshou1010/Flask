from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager



class UserProfile(BaseModel, Base):
    __tablename__ = "user_profile"
    id = Column(types.Integer, primary_key=True, autoincrement=True)
    account = Column(types.String(40), nullable=False, unique=True)
    hash_password = Column(types.String(255), nullable=False)
    phone_number = Column(types.VARCHAR(20), nullable=True)
    email = Column(types.VARCHAR(254), nullable=False, unique=True)
    token = Column(types.String(2000), nullable=True)