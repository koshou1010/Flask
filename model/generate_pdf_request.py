from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager



class GeneratePDFRequest(Base):
    __tablename__ = "generate_pdf_request"
    id = Column(types.Integer, primary_key=True, autoincrement=True)
    status_flag = Column(types.Boolean, nullable=True,default=False)
    json_path = Column(types.String(255), nullable=True)
    poincare_path = Column(types.String(255), nullable=True)
    pdf_path = Column(types.String(255),nullable=True)