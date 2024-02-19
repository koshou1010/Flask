from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager



class File(Base):
    __tablename__ = "file"
    record_id = Column(types.Integer, primary_key=True, autoincrement=True)
    report_table_index = Column(types.Integer)
    zip_path = Column(types.String(255))
    zip_filename = Column(types.String(55))