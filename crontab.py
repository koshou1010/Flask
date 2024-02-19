import os
import zipfile
import time
import sys
import traceback
import application
from sqlalchemy.orm import sessionmaker
from utility.mail_center.model import send_email
from utility.sql_alchemy.globals import sqlAlchemy_manager
from utility.mongodb_.globals import mongodb_manager
from model.report import Report
from model.file import File
from utility.logger.globals import logger_manager
from application.controller import start_process
LockName = 'cronjob_report_generator_lock'


def check_cpu_usage():
    """
    Check Currently CPU usage.
    return true if usage greater than 35.5, which is not a good time to do job.
    """
    import psutil
    cpu_usage = psutil.cpu_percent(interval=1, percpu=False)
    logger_manager.logger.info('cpu usage: {}'.format(cpu_usage))
    return cpu_usage > 35.5


class DataBaseInit:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    MONGO_DATABASE_URI = os.getenv('MONGO_DATABASE_URI')
    MONGO_DATABASE_NAME = os.getenv('MONGO_DATABASE_NAME')
    MONGO_DATABASE_COLLECTION = os.getenv('MONGO_DATABASE_COLLECTION')

    def __init__(self) -> None:
        self.mysql_connect()
        self.mongo_connect()

    def mysql_connect(self):
        from utility.sql_alchemy import setup
        setup(self.SQLALCHEMY_DATABASE_URI)

    def mongo_connect(self):
        from utility.mongodb_ import setup
        setup(host=self.MONGO_DATABASE_URI,
              testing=False,
              db_name=self.MONGO_DATABASE_NAME,
              collection=self.MONGO_DATABASE_COLLECTION
              )


class CrontabController:
    def __init__(self, mode):
        DataBaseInit()
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.mysql_engine_url = os.getenv('SQLALCHEMY_DATABASE_URI')
        self.mongodb_engine_url = os.getenv('MONGO_DATABASE_URI')
        self.mongo_db_name = os.getenv('MONGO_DATABASE_NAME')

    def create_session(self):
        Session = sessionmaker(bind=self.mysql_manage.engine)
        session = Session()
        return session

    def explode_zip_file(self, file_list: list, zip_path: str):
        for file in file_list:
            with zipfile.ZipFile(file, 'r') as zf:
                for name in zf.namelist():
                    zf.extract(name, path=zip_path)

    def query_data_zip_path(self, report_table_index: int) -> str:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(File).filter_by(
                report_table_index=report_table_index).all()
            for i in query_result:
                zip_path = i.zip_path
            session.commit()
        return zip_path

    def query_data_same_rtb_zf(self, report_table_index: int) -> list:
        '''
        get zip filename which are same report table index
        '''

        all_file_list = []
        with sqlAlchemy_manager.Session() as session:
            res = session.query(File).filter_by(
                report_table_index=report_table_index).all()
            for i in res:
                all_file_list.append(os.path.join(i.zip_path, i.zip_filename))
            session.commit()
        return all_file_list

    def query_not_generate_index(self, end_flag: bool) -> tuple:
        '''
        end_flag column, True or None
        1. find end_flag == True -> means client update all file done
        2. find in_update_done['flag'] == True and not result_message index
        3. if find it, break early
        '''

        result_list = []
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(Report).filter_by(end_flag=end_flag).all()
            if query_result == []:
                return False, None
            for i in query_result:
                # logger_manager.logger.info(i.record_id, i.end_flag, i.in_queue)
                if i.generate_status['in_update_done']['flag'] == True and not i.result_message:
                    result_list.append(i.record_id)
                    # if result_list != 0:
                    #     break
            session.commit()
        return True, result_list

    def query_data_algorithm_input(self, content: dict) -> tuple:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(
                content['table']).get(content['primary_key'])
            algorithm_input = query_result.algorithm_input
            report_code = query_result.report_code
            session.commit()
        return algorithm_input, report_code

    def query_data_result_message(self, primary_key: int) -> str:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(Report).get(
                primary_key).result_message
            session.commit()
        return query_result

    def lock(self):
        logger_manager.logger.info("Lock.")
        lock_file_name = os.path.join(self.file_path, LockName)
        lock = str(int(round(time.time() * 1000)))
        with open(lock_file_name, "w") as lock_file:
            logger_manager.logger.info("Open Lock file.")
            lock_file.write(lock)
        logger_manager.logger.info("Write Lock: {}".format(lock))

    def unlock(self):
        logger_manager.logger.info("UnLock.")
        lock_file_name = os.path.join(self.file_path, LockName)
        if os.path.exists(lock_file_name):
            os.remove(lock_file_name)
            logger_manager.logger.info("Remove Lock file.")

    def isLocked(self):
        logger_manager.logger.info("Check Lock File Exist.")
        lock_file_name = os.path.join(self.file_path, LockName)
        islocked = True if os.path.exists(lock_file_name) else False
        logger_manager.logger.info(
            '{} exists :{}'.format(lock_file_name, islocked))
        return islocked

    def update_generate_result_message(self, data, primary_key):
        with sqlAlchemy_manager.Session() as session:
            session.query(Report).filter_by(record_id=primary_key).update(
                {Report.result_message: data})
            session.commit()
            session.close()

    def excute_action(self):
        result, report_table_index_list = self.query_not_generate_index(True)
        logger_manager.logger.info(f'get {result}, report table index : {report_table_index_list}')
        while result and len(report_table_index_list) != 0:
            logger_manager.logger.info(f'start report table index : {report_table_index_list[0]}')
            report_table_index = report_table_index_list[0]
            zip_path = self.query_data_zip_path(report_table_index)
            all_file_list = self.query_data_same_rtb_zf(report_table_index)
            self.explode_zip_file(all_file_list, zip_path)
            content = {
                "request_type": "health_server_request",
                "table": Report,
                "primary_key": report_table_index,
                "zip_path": zip_path
            }
            algorithm_input, report_code = self.query_data_algorithm_input(
                content)
            start_process(content)
            report_table_index_list.pop(0)
        else:
            logger_manager.logger.info('There are not find preapared report_table_index want to generate')


if __name__ == '__main__':
    mode = os.getenv('MODE')
    logger_manager.logger.info('Start Crontab...')
    if check_cpu_usage():
        logger_manager.logger.info(
            "CPU usage is too high, pass migration now.")
    else:
        crontab_controller = CrontabController(mode)
        if crontab_controller.isLocked():
            logger_manager.logger.info("Currently Locked.")
        else:
            try:
                crontab_controller.lock()
                # crontab_controller.test()
                crontab_controller.excute_action()
            finally:
                crontab_controller.unlock()
