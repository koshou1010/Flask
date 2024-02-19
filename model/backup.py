from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager



class BackUp(Base):
    __tablename__ = "backup"
    id = Column(types.Integer, primary_key=True, autoincrement=True)
    file_path = Column(types.String(255), nullable=False)
    type = Column(types.String(255), nullable=False)
    back_up_flag = Column(types.Boolean, nullable=False, default=False)