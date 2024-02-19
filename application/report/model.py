from utility.sql_alchemy.globals import sqlAlchemy_manager
from model.report import Report
from model.file import File
import os, zipfile


class ReportContent:
    

    @classmethod
    def get_all(self):
        with sqlAlchemy_manager.Session() as session:
            res = session.query(Report).filter(Report.valid_flag==True).all()
        return res
    

    @classmethod
    def query_report_by_id(self, id: int):
        with sqlAlchemy_manager.Session() as session:
            res = session.query(Report).filter_by(
                record_id=id
            ).first()
        return res    
    
    @classmethod
    def query_file_by_report_id(self, id: int):
        with sqlAlchemy_manager.Session() as session:
            res = session.query(File).filter_by(
                report_table_index=id
            ).all()
        return res    
    
    @classmethod
    def compress_all_file(self, zip_filename: str, file_list: list) :
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i in file_list: 
                zf.write(i, os.path.basename(i))   

