from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager


class LineLink(Base):
    __tablename__ = "line_link"
    id = Column(types.Integer, primary_key=True, autoincrement=True)
    line_id = Column(types.String(255), nullable=False)
    uuid = Column(types.Integer, ForeignKey('user.uuid'), nullable=True)
    create_time = Column(types.DateTime, nullable=False, default=datetime.now)
    linked_time = Column(types.DateTime, nullable=True)
    link_task_status = Column(types.JSON)
    valid_flag = Column(types.Boolean, nullable=False, default=True)
