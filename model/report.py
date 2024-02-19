from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager



class Report(BaseModel, Base):
    __tablename__ = "report"
    record_id = Column(types.Integer, primary_key=True, autoincrement=True)
    user_id = Column(types.Integer)
    user_info = Column(types.JSON)
    health_server_got_generate_request_time = Column(types.BigInteger)
    health_server_post_create_time = Column(types.BigInteger)
    report_server_got_post_create_time = Column(types.BigInteger)
    algorithm_input = Column(types.JSON)
    report_code = Column(types.String(55))
    end_flag = Column(types.Boolean)
    generate_status = Column(types.JSON)
    review_status = Column(types.JSON)
    result_message = Column(types.JSON)
    reviewed_path = Column(types.String(255))
    pdf_path = Column(types.String(255))
    locale = Column(types.String(255), nullable=True, default="tw") # 語系
    units = Column(types.String(255), nullable=True, default= "mm") # inch英制  mm公制
    algo_version = Column(types.String(255), nullable=False)
    golden_sample = Column(types.Boolean, nullable=True, default=False)