import time
import os
import json
import re
import zipfile
import sys
import traceback
from datetime import datetime
from utility.algorithms.report.ExerciseReportGenerator import ExerciseReportGenerator
from utility.algorithms.report.SleepQualityReportGenerator import SleepQualityReportGenerator
from utility.algorithms.report.CardiovascularHealthReportGenerator import CardiovascularHealthReportGenerator
from application.setting import LOCALE_TRANSFER_DICT, ZIP_FILE_PATH_HEALTH_SERVER, E001V1_FILES_PATH, PDF_A002V2_PATH, PDF_S001V1_PATH, PDF_E001V1_PATH
import application.setting as setting
from application.algorithm_interface.model import choose_algorithm_type
from application.generate_pdf_interface.model import fake_choose_generate_pdf_version
from ..model import RequestTemplate
from utility.logger.globals import logger_manager
from utility.mail_center.model import send_email
from model.report import Report
from model.report_sleep_statistic import ReportSleepStatistic
from model.user import User
from model.file import File
from model.backup import BackUp
from utility.sql_alchemy.globals import sqlAlchemy_manager
from sqlalchemy import func
from utility.mongodb_.globals import mongodb_manager

BASEDIR = os.path.dirname(os.path.realpath(__file__))

S001V1_LOCALE_JSON_PATH = os.path.join(
    BASEDIR, '..', 'reportgen', 'locale', 's001v1.json')
E001V1_LOCALE_JSON_PATH = os.path.join(
    BASEDIR, '..', 'reportgen', 'locale', 'e001v1.json')
A002V2_LOCALE_JSON_PATH = os.path.join(
    BASEDIR, '..', 'reportgen', 'locale', 'a002v2.json')


class HealthServerRequestAction(RequestTemplate):

    default_user: str = "server"

    def __init__(self):
        self.report_generating = False
        self.report_generate_progress = {
            "in_create": {"flag": 0, "time": None},
            "in_create_done": {"flag": 0, "time": None},
            "in_send": {"flag": 0, "time": None},
            "in_send_done": {"flag": 0, "time": None},
            "in_update": {"flag": 0, "time": None},
            "in_update_done": {"flag": 0, "time": None},
            "in_algorithm": {"flag": 0, "time": None},
            "in_algorithm_done": {"flag": 0, "time": None},
            "in_generate_pdf": {"flag": 0, "time": None},
            "in_generate_pdf_done": {"flag": 0, "time": None}
        }
        self.algorithm_setting_map = {
            'S001V1': {'time_format': '%Y%m%d %H%M%S'},
            'E001V1': {'time_format': '%Y%m%d %H%M%S'},
            'A002V2': {'time_format': '%Y%m%d'}
        }

        self.data_completed_map = {
            'create': ["report_code", "user_id", "health_server_got_generate_request_time", "health_server_post_create_time", "user_info", "algorithm_input", "golden_sample"],
            'send': ["report_table_index"],
            'update': ["report_table_index", "end_flag"]
        }

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
                golden_sample=data['golden_sample'],
                create_user=self.default_user,
                update_user=self.default_user
            )
            session.add(insert_data)
            session.commit()
            pk = insert_data.record_id
        return pk

    def update_data_generate_status(self, primary_key: int, status: str):
        with sqlAlchemy_manager.Session() as session:
            target_flag_key = '$.{}.{}'.format(status, 'flag')
            target_flag_time = '$.{}.{}'.format(status, 'time')
            session.query(Report).filter_by(record_id=primary_key).update(
                {Report.generate_status: func.json_set(Report.generate_status, target_flag_key, True)})
            session.query(Report).filter_by(record_id=primary_key).update(
                {Report.generate_status: func.json_set(Report.generate_status, target_flag_time, int(time.time()))})
            session.commit()

    def query_data_primary_key(self, data: str) -> int:
        with sqlAlchemy_manager.Session() as session:
            query = session.query(Report).get(int(data))
        return query

    def create_file(self, data: dict):
        with sqlAlchemy_manager.Session() as session:
            insert_data = File(
                report_table_index=data['report_table_index'],
                zip_path=data['zip_path'],
                zip_filename=data['zip_filename']
            )
            session.add(insert_data)
            session.commit()

    def update_end_flag(self, end_flag: bool, report_table_index: str):
        with sqlAlchemy_manager.Session() as session:
            session.query(Report).filter_by(
                record_id=report_table_index).update({Report.end_flag: end_flag})
            session.commit()

    def make_dir(self, path):
        os.makedirs(path, exist_ok=True)

    def check_file_endswith(self, file: str, kind: str) -> bool:
        return file.endswith(kind)

    def explode_zip_file(self, file_list: list, zip_path: str):
        for file in file_list:
            with zipfile.ZipFile(file, 'r') as zf:
                for name in zf.namelist():
                    zf.extract(name, path=zip_path)

    def report_generate_progress_reset(self):
        self.report_generate_progress = {
            "in_create": {"flag": 1, "time": int(time.time())},
            "in_create_done": {"flag": 0, "time": None},
            "in_send": {"flag": 0, "time": None},
            "in_send_done": {"flag": 0, "time": None},
            "in_update": {"flag": 0, "time": None},
            "in_update_done": {"flag": 0, "time": None},
            "in_algorithm": {"flag": 0, "time": None},
            "in_algorithm_done": {"flag": 0, "time": None},
            "in_generate_pdf": {"flag": 0, "time": None},
            "in_generate_pdf_done": {"flag": 0, "time": None}
        }

    def query_data_generate_status(self, primary_key: str) -> dict:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(Report).get(
                primary_key).generate_status
            session.commit()
        return query_result

    def query_data_result_message(self, primary_key: str) -> str:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(Report).get(
                primary_key).result_message
            session.commit()
        return query_result

    def query_generate_status(self, primary_key: str) -> dict:
        generate_status = self.query_data_generate_status(primary_key)
        result_message = self.query_data_result_message(primary_key)
        if not result_message:
            if generate_status["in_algorithm"]["flag"] == 0:
                return {"error_message": "algorithm didn't start"}, 403
            if generate_status["in_algorithm"]["flag"] == 1 and generate_status["in_algorithm_done"]["flag"] == 0:
                return {"error_message": "algorithm running"}, 403
            return {"error_message": "algorithm didn't have result"}, 403
        if 'status' not in result_message:
            return {"exception_error": result_message}, 405
        if not result_message['status']:
            return {"error_message": result_message["message"]}, 405
        return {'time_record': generate_status, 'result_message': result_message}

    def query_pdf_path(self, primary_key: int) -> dict:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(Report).get(primary_key).pdf_path
        return query_result

    def query_user(self, data):
        with sqlAlchemy_manager.Session() as session:
            query = session.query(User).filter(
                User.uuid == int(data['user_info']['id'])).all()
        print("query")
        print(query)
        return query

    def create_user(self, data: dict):
        # session.add(table(**data))
        if not self.query_user(data):
            with sqlAlchemy_manager.Session() as session:
                insert_data = User(
                    create_time=int(time.time()),
                    uuid=int(data['user_info']['id']),
                    name=data['user_info']['name'],
                    sex=data['user_info']['gender'],
                    age=int(float(data['user_info']['age'])),
                    birthday=data['user_info']['birthday'],
                    height=int(float(data['user_info']['height'])),
                    weight=int(float(data['user_info']['weight']))
                )
                session.add(insert_data)
                session.commit()


class HealthServerReportGenerator:
    def __init__(self) -> None:
        self.manual_reviewed = True
        self.algorithm_setting_map = {
            'S001V1': {'time_format': '%Y%m%d %H%M%S'},
            'E001V1': {'time_format': '%Y%m%d %H%M%S'},
            'A002V2': {'time_format': '%Y%m%d'}
        }

    def query_locale(self, id: int) -> str:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(Report).get(id).locale
            session.commit()
        return query_result

    def query_data_result_message(self, primary_key: str) -> str:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(Report).get(
                primary_key).result_message
            session.commit()
        return query_result

    def update_data_generate_status(self, primary_key: int, status: str):
        with sqlAlchemy_manager.Session() as session:
            target_flag_key = '$.{}.{}'.format(status, 'flag')
            target_flag_time = '$.{}.{}'.format(status, 'time')
            session.query(Report).filter_by(record_id=primary_key).update(
                {Report.generate_status: func.json_set(Report.generate_status, target_flag_key, True)})
            session.query(Report).filter_by(record_id=primary_key).update(
                {Report.generate_status: func.json_set(Report.generate_status, target_flag_time, int(time.time()))})
            session.commit()

    def update_generate_result_message(self, primary_key: int, data: dict):
        with sqlAlchemy_manager.Session() as session:
            session.query(Report).filter_by(record_id=primary_key).update(
                {Report.result_message: data})
            session.commit()
        pass

    def update_generate_pdf_path(self, path: str, primary_key: int):
        with sqlAlchemy_manager.Session() as session:
            session.query(Report).filter_by(
                record_id=primary_key).update({Report.pdf_path: path})
            session.commit()

    def query_data_algorithm_input(self, data: dict):
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(
                data['table']).get(data['primary_key'])
            algorithm_input = query_result.algorithm_input
            report_code = query_result.report_code
            session.commit()
            session.close()
        return algorithm_input, report_code

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

    def create_backup_data(self, file_path: str, type: str):
        with sqlAlchemy_manager.Session() as session:
            insert_data = BackUp(
                file_path=file_path,
                back_up_flag=False,
                type=type
            )
            session.add(insert_data)
            session.commit()

    def update_backup_flag(self, id: int):
        with sqlAlchemy_manager.Session() as session:
            session.query(BackUp).filter_by(
                id=id).update({BackUp.back_up_flag: True})
            session.commit()
            session.close()

    def start_process_entrance(self, content: dict):
        self.report_generating = True
        self.locale = self.query_locale(content['primary_key'])
        all_file_list = self.query_data_same_rtb_zf(content['primary_key'])
        algorithm_input, report_code = self.query_data_algorithm_input(content)
        try:
            report_code_and_algorithm_input = self.prepare_algorithm_input(
                content)
            algorithm_result, report_code, user_info = self.start_algorithm_part(
                report_code_and_algorithm_input, content)
        except Exception as e:
            cl, exc, tb = sys.exc_info()
            exception_message = {
                "status": False,
                "type": "algorithm",
                'message':""
            }
            for line in traceback.format_tb(tb):
                logger_manager.logger.info('Exception ---> {}'.format(str(line)))
                exception_message['message'] = f"{exception_message['message']}\n{str(line)}"
            exception_message['message'] = f"{exception_message['message']}\n{str(e)}"
            self.update_generate_result_message(
                content['primary_key'], exception_message)
            msg = {
                "message": exception_message['message'],
                "all_file_list": all_file_list,
                "report_code": report_code,
                "algorithm_input": algorithm_input,
                "type": exception_message["type"]
            }
            send_email(
                "Report Generate Has an Exception(此為系統自動通知信，請勿直接回信)", msg)
            return False

        try:
            if algorithm_result['status']:
                if self.manual_reviewed:
                    self.start_generate_pdf_part(
                        content, algorithm_result['message'], report_code, user_info)
        except Exception as e:
            cl, exc, tb = sys.exc_info()
            exception_message = {
                "status": False,
                "type": "pdf",
                "message": ""
            }
            for line in traceback.format_tb(tb):
                logger_manager.logger.info('Exception ---> {}'.format(str(line)))
                exception_message['message'] = f"{exception_message['message']}\n{str(line)}"
            exception_message['message'] = f"{exception_message['message']}\n{str(e)}"
            result_message = self.query_data_result_message(
                content['primary_key'])
            json_path = [result_message['message']]
            self.update_generate_result_message(
                content['primary_key'], exception_message)
            msg = {
                "message": exception_message['message'],
                "all_file_list": json_path,
                "report_code": report_code,
                "algorithm_input": algorithm_input,
                "type": exception_message["type"]
            }
            send_email(
                "Report Generate Has an Exception(此為系統自動通知信，請勿直接回信)", msg)
            return False
        self.report_generating = False

    def transfer_timestamp(self, algorithm_input: dict, time_format: str):
        for key in algorithm_input.keys():
            if key.endswith('_tt'):
                algorithm_input[key] = datetime.fromtimestamp(
                    algorithm_input[key]/1000).strftime(time_format)
        return algorithm_input

    def assign_locale_units_timezone(self, user_info: dict):

        if user_info['locale'] not in LOCALE_TRANSFER_DICT.keys():
            user_info['language'] = LOCALE_TRANSFER_DICT['tw']
        else:
            user_info['language'] = LOCALE_TRANSFER_DICT[user_info['locale']]
        if user_info['units'] not in LOCALE_TRANSFER_DICT.keys():
            user_info['unit'] = LOCALE_TRANSFER_DICT['mm']
        else:
            user_info['unit'] = LOCALE_TRANSFER_DICT[user_info['units']]

    def prepare_algorithm_input(self, content: dict) -> tuple:
        logger_manager.logger.info('Start Prepare Algorithm Input')
        algorithm_input, report_code = self.query_data_algorithm_input(content)
        algorithm_input = self.transfer_timestamp(
            algorithm_input, self.algorithm_setting_map[report_code]['time_format'])
        self.assign_locale_units_timezone(algorithm_input['user_info'])
        logger_manager.logger.info('report code : {}'.format(report_code))
        if report_code == 'S001V1':
            return (report_code), (algorithm_input['step_test_start_tt'], algorithm_input['step_test_end_tt'], algorithm_input['exercise_start_tt'], algorithm_input['exercise_end_tt'], algorithm_input['user_info'])
        elif report_code == 'E001V1':
            return (report_code), (algorithm_input['report_start_tt'], algorithm_input['report_end_tt'], algorithm_input['user_info'])
        elif report_code == 'A002V2':
            return (report_code), (algorithm_input['report_start_tt'], algorithm_input['report_end_tt'], algorithm_input['user_info'])

    def start_algorithm_part(self, report_code_and_algorithm_input, content):
        report_code = report_code_and_algorithm_input[0]
        algorithm_input = report_code_and_algorithm_input[1]
        user_info = algorithm_input[-1]
        logger_manager.logger.info('Start Algorithm')
        self.update_data_generate_status(
            content['primary_key'], 'in_algorithm')
        if report_code == 'S001V1':
            algorithm_result = choose_algorithm_type(report_code, content['zip_path'])(
                algorithm_input[0], algorithm_input[1], algorithm_input[2], algorithm_input[3], user_info)
        elif report_code == 'E001V1':
            algorithm_result = choose_algorithm_type(report_code, content['zip_path'])(
                algorithm_input[0], algorithm_input[1], user_info)
        elif report_code == 'A002V2':
            history_list = mongodb_manager.query_data_id(user_info['id'])
            algorithm_result = choose_algorithm_type(report_code, content['zip_path'])(
                algorithm_input[0], algorithm_input[1], user_info, report_code, history_list)
            if algorithm_result['status'] is True:
                history_result = {"history": algorithm_result['record'][0]}
                history_result["history"]['score'] = int(
                    history_result["history"]['score'])
                history_result['id'] = user_info['id']
                mongodb_manager.create_data(history_result)
        self.update_generate_result_message(
            content['primary_key'], algorithm_result)
        self.update_data_generate_status(
            content['primary_key'], 'in_algorithm_done')
        logger_manager.logger.info('End Algorithm')
        return algorithm_result, report_code, user_info

    def calculate_sleep_stage(self, sleep_stage_list: list) -> dict:
        data = {}
        data['total_sleep_hrs'] = round(
            len(sleep_stage_list)/60, 2)  # minutes/60 = hours
        data['missing_times'] = sleep_stage_list.count(-1)
        sleep_stage_list_without_missing = len(
            sleep_stage_list)-data['missing_times']
        data['total_sleep_hrs_without_missing'] = round(
            sleep_stage_list_without_missing/60, 2)
        data['awake_times'] = sleep_stage_list.count(0)
        data['rem_times'] = sleep_stage_list.count(1)
        data['light_times'] = sleep_stage_list.count(2)
        data['deep_times'] = sleep_stage_list.count(3)

        data['awake_per_with_awake'] = round(
            data['awake_times']/sleep_stage_list_without_missing*100, 2)
        data['rem_per_with_awake'] = round(
            data['rem_times']/sleep_stage_list_without_missing*100, 2)
        data['light_per_with_awake'] = round(
            data['light_times']/sleep_stage_list_without_missing*100, 2)
        data['deep_per_with_awake'] = round(
            data['deep_times']/sleep_stage_list_without_missing*100, 2)

        sleep_stage_list_without_missing_and_awake = len(sleep_stage_list)-data['missing_times']-data['awake_times']
        if sleep_stage_list_without_missing_and_awake == 0:
            data['rem_per_without_awake'] = 0
            data['light_per_without_awake'] = 0
            data['deep_per_without_awake'] = 0
            return data
        data['rem_per_without_awake'] = round(data['rem_times']/sleep_stage_list_without_missing_and_awake*100, 2)
        data['light_per_without_awake'] = round(data['light_times']/sleep_stage_list_without_missing_and_awake*100, 2)
        data['deep_per_without_awake'] = round(data['deep_times']/sleep_stage_list_without_missing_and_awake*100, 2)
        return data

    def create_sleep_statistic(self, report_id: int, data: dict):
        with sqlAlchemy_manager.Session() as session:
            insert_data = ReportSleepStatistic(
                report_id=report_id,
                total_sleep_hrs=data['total_sleep_hrs'],
                total_sleep_hrs_without_missing=data['total_sleep_hrs_without_missing'],
                missing_times=data['missing_times'],
                awake_times=data['awake_times'],
                rem_times=data['rem_times'],
                light_times=data['light_times'],
                deep_times=data['deep_times'],
                awake_per_with_awake=data['awake_per_with_awake'],
                rem_per_with_awake=data['rem_per_with_awake'],
                light_per_with_awake=data['light_per_with_awake'],
                deep_per_with_awake=data['deep_per_with_awake'],
                rem_per_without_awake=data['rem_per_without_awake'],
                light_per_without_awake=data['light_per_without_awake'],
                deep_per_without_awake=data['deep_per_without_awake'],
                create_user='server',
                update_user='server'
            )
            session.add(insert_data)
            session.commit()
            return insert_data.id

    def start_generate_pdf_part(self, content: dict, json_output_path: str, report_code: str, user_info: dict):
        self.filename = '{0}_{1:05d}_{2}.pdf'.format(
            report_code, int(user_info['id']), str(int(time.time())))
        self.update_data_generate_status(
            content['primary_key'], 'in_generate_pdf')
        logger_manager.logger.info(
            'json_output_path: {}'.format(json_output_path))
        print('json_output_path: {}'.format(json_output_path))
        logger_manager.logger.info('Start {} PDF'.format(report_code))
        print('Start {} PDF'.format(report_code))
        with open(json_output_path, 'r', encoding='utf-8') as f:
            report_json = json.load(f)
        generate_pdf_version_instanse = fake_choose_generate_pdf_version(
            report_code)
        if report_code == 'S001V1':
            with open(S001V1_LOCALE_JSON_PATH, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            locale_data_selected = locale_data[self.locale]
            pdf_path = generate_pdf_version_instanse.genReport(
                report_json, self.filename, '', locale=self.locale, locale_data=locale_data_selected)
            self.update_generate_pdf_path(os.path.join(
                PDF_S001V1_PATH, self.filename), content['primary_key'])
        elif report_code == 'E001V1':
            sleep_stage_list = report_json['sleepingState']['Stage']
            data = self.calculate_sleep_stage(sleep_stage_list)
            self.create_sleep_statistic(content['primary_key'], data)

            with open(E001V1_LOCALE_JSON_PATH, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            locale_data_selected = locale_data[self.locale]
            self.temp_png_path = os.path.join(
                E001V1_FILES_PATH, str(user_info['id']))
            if not os.path.exists(self.temp_png_path):
                os.mkdir(self.temp_png_path)
            pdf_path = generate_pdf_version_instanse.genReport(
                report_json, self.filename, self.temp_png_path, locale=self.locale, locale_data=locale_data_selected)
            self.update_generate_pdf_path(os.path.join(
                PDF_E001V1_PATH, self.filename), content['primary_key'])
        elif report_code == 'A002V2':
            with open(A002V2_LOCALE_JSON_PATH, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            locale_data_selected = locale_data[self.locale]
            pdf_path = generate_pdf_version_instanse.genReport(
                report_json, self.filename, locale=self.locale, locale_data=locale_data_selected)
            self.update_generate_pdf_path(os.path.join(
                PDF_A002V2_PATH, self.filename), content['primary_key'])
        self.update_data_generate_status(
            content['primary_key'], 'in_generate_pdf_done')
        print('End {} PDF.'.format(report_code))
        logger_manager.logger.info('End {} PDF.'.format(report_code))
        self.create_backup_data(pdf_path, report_code)
