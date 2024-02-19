
# from .controller import main as application_root
import time
import os
from flask import Flask
from application.setting import FOLDER_CONTROLLER_LIST
from flasgger import Swagger
from utility.sql_alchemy.globals import sqlAlchemy_manager
from model.token import Token
from model.report import Report
from model import *
from utility.algorithms.report.version import __version__


def check_folder_path():
    for path in FOLDER_CONTROLLER_LIST:
        if not os.path.exists(path):
            os.mkdir(path)


class MakeFakeDataForTesting:
    def __init__(self) -> None:
        self.create_permission()

    def create_permission(self):
        with sqlAlchemy_manager.Session() as session:
            insert_data = Token(
                token="711565b38b1c85510998e256e74b7cc73d558b7cbe77ad52ba0f1b3da276a597",
                customer="KoshouDevelop",
                create_time=int(time.time()),
                permission="normal",
                create_user="test",
                update_user="test"
            )
            session.add(insert_data)
            session.commit()

    def create_report(self, data: dict) -> int:
        with sqlAlchemy_manager.Session() as session:
            insert_data = Report(
                user_id=data['user_id'],
                user_info=data['user_info'],
                health_server_got_generate_request_time=data['health_server_got_generate_request_time'],
                health_server_post_create_time=data['health_server_post_create_time'],
                report_server_got_post_create_time=data['report_server_got_post_create_time'],
                algorithm_input=data['algorithm_input'],
                report_code=data['report_code'],
                generate_status=data['generate_status'],
                locale=data['locale'],
                units=data['units'],
                algo_version=data['algo_version'],
                create_user = "test",
                update_user = "test"
            )
            session.add(insert_data)
            session.commit()
            current_record_id = insert_data.record_id
        return current_record_id

    def update_result_message(self, pk: int, data: str):
        with sqlAlchemy_manager.Session() as session:
            session.query(Report).filter_by(record_id=pk).update(
                {Report.result_message: data})
            session.commit()

    def update_generate_result_message(self, primary_key: int, data: dict):
        with sqlAlchemy_manager.Session() as session:
            session.query(Report).filter_by(record_id=primary_key).update(
                {Report.result_message: data})
            session.commit()
        pass


def make_fake_data_for_unit_test(mode):
    from application.health_server_request.model import HealthServerRequestAction
    if mode == 'test':
        create_db()
        health_server_request = HealthServerRequestAction()
        instanse = MakeFakeDataForTesting()
        data = {"report_code": "S001V1", "user_id": 7, "health_server_got_generate_request_time": 1660094681353, "health_server_post_create_time": 1664265075021, "user_info": {"id": "7", "name": "koshou", "email": "koshou@koshou.com", "gender": "男", "height": "176", "weight": "90", "birthday": "1996/10/10", "age": "25"},
                "algorithm_input": {
                    "step_test_start_tt": 1662111836963, "step_test_end_tt": 1662112234177, "exercise_start_tt": 1662112291507, "exercise_end_tt": 1662114091512,
                    "user_info": {
                        "locale": "en", "units": "mm",
                        "id": "7", "name": "koshou", "email": "koshou@koshou.com", "gender": "男", "height": "176", "weight": "90", "birthday": "1996/10/10", "age": "25"}}}

        data['report_server_got_post_create_time'] = int(time.time())
        data['generate_status'] = health_server_request.report_generate_progress
        data['algo_version'] = __version__
        # if no locale and units, setting default
        if 'locale' not in data['algorithm_input']['user_info'].keys() or not data['algorithm_input']['user_info']['locale']:
            data['locale'] = "tw"
        else:
            data['locale'] = data['algorithm_input']['user_info']['locale']
        if 'units' not in data['algorithm_input']['user_info'].keys() or not data['algorithm_input']['user_info']['units']:
            data['units'] = "mm"
        else:
            data['units'] = data['algorithm_input']['user_info']['units']
        pk = instanse.create_report(data)
        result_message = {
            "status": True, "message": "C:\\projects\\ReportGeneratorServer\\utility\\algorithms\\report\\ExerciseReportOutput\\7\\20221004\\Report_2022100411(7).json"}
        instanse.update_result_message(pk, result_message)
        pk = instanse.create_report(data)
        pk = instanse.create_report(data)
        result_message = {"record": [], "status": False,
                          "message": "The Number of the Day is Not Enough"}
        instanse.update_generate_result_message(3, result_message)


def create_db():
    sqlAlchemy_manager.create_all()


def create_app(mode: str):
    check_folder_path()
    from utility.logger.globals import logger_manager
    logger_manager.logger.info('flask server setup')
    app = Flask(__name__)

    from config import config
    app.config.from_object(config[mode])
    config[mode].init_app(app)
    make_fake_data_for_unit_test(mode)

    from .controller import main
    app.register_blueprint(main)

    from .health_server_request import health_server_request
    app.register_blueprint(health_server_request)

    from .login import login
    app.register_blueprint(login)

    from .manual_review import manual_review
    app.register_blueprint(manual_review)

    from .generate_pdf_request import generate_pdf_request
    app.register_blueprint(generate_pdf_request)


    from .token import token
    app.register_blueprint(token)

    from .statistic import statistic
    app.register_blueprint(statistic)
    
    from .report import report
    app.register_blueprint(report)
    
    return app
