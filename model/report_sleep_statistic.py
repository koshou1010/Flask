from utility.sql_alchemy.base import BaseModel, Column, ForeignKey, types, datetime
from utility.sql_alchemy.globals import Base, sqlAlchemy_manager


class ReportSleepStatistic(BaseModel, Base):
    __tablename__ = "report_sleep_statistic"
    id = Column(types.BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(types.Integer, ForeignKey('report.record_id'), nullable=False)
    total_sleep_hrs = Column(types.Float, nullable=False)
    total_sleep_hrs_without_missing = Column(types.Float, nullable=False)
    missing_times = Column(types.Integer, nullable=False)
    awake_times = Column(types.Integer, nullable=False)
    rem_times = Column(types.Integer, nullable=False)
    light_times = Column(types.Integer, nullable=False)
    deep_times = Column(types.Integer, nullable=False)  

    awake_per_with_awake = Column(types.Float, nullable=False)
    rem_per_with_awake = Column(types.Float, nullable=False)
    light_per_with_awake = Column(types.Float, nullable=False)
    deep_per_with_awake = Column(types.Float, nullable=False)
    
    rem_per_without_awake = Column(types.Float, nullable=False)
    light_per_without_awake = Column(types.Float, nullable=False)
    deep_per_without_awake = Column(types.Float, nullable=False)
    

