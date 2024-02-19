from utility.sql_alchemy.globals import sqlAlchemy_manager
from model.report import Report
from model.report_sleep_statistic import ReportSleepStatistic



class SleepStatisticContent:
    
    
    @classmethod
    def query_report_by_report_id(self, id: int):
        with sqlAlchemy_manager.Session() as session:
            res = session.query(Report).filter_by(
                record_id=id
            ).first()
        return res    

    @classmethod
    def query_sleep_statistic_by_report_id(self, id: int):
        with sqlAlchemy_manager.Session() as session:
            res = session.query(ReportSleepStatistic).filter_by(
                report_id=id
            ).first()
        return res    
    

    @classmethod
    def get_all(self):
        with sqlAlchemy_manager.Session() as session:
            res = session.query(ReportSleepStatistic).filter(ReportSleepStatistic.valid_flag==True).all()
        return res