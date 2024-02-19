import time
import os
import io
from flask import Blueprint, request, send_file, abort
from .model import HealthServerRequestAction
from application.setting import ZIP_FILE_PATH_HEALTH_SERVER, ROOT_PATH
from utility.wrapper.model import verify_report_server_token, check_data_completed, exception_handler
from utility.logger.globals import logger_manager
from utility.algorithms.report.version import __version__

main = Blueprint('health_server_request', __name__)

health_server_request = HealthServerRequestAction()


@main.route('/api/report/generate/create', methods=['POST'])
@verify_report_server_token
@check_data_completed('create', health_server_request.data_completed_map)
@exception_handler
def report_generate_create():
    health_server_request.report_generate_progress_reset()
    data = request.get_json()
    data['report_server_got_post_create_time'] = int(time.time())
    data['generate_status'] = health_server_request.report_generate_progress
    data['algo_version'] = __version__

    # if no locale and units, setting default
    data['locale'] = data['algorithm_input']['user_info']['locale'] = data['algorithm_input']['user_info'].get('locale') or "tw"
    data['units'] = data['algorithm_input']['user_info']['units'] = data['algorithm_input']['user_info'].get('units') or "mm"
    data['golden_sample'] = 'golden_sample' in data

    health_server_request.create_user(data)
    current_record_id = health_server_request.create_report(data)
    health_server_request.update_data_generate_status(
        current_record_id, 'in_create_done')
    logger_manager.logger.info(
        'create - > {}'.format({'sucess_message': {'report_table_index': current_record_id}}))
    return {"sucess_message": {"report_table_index": current_record_id}}


@main.route('/api/report/generate/send', methods=['POST'])
@verify_report_server_token
@check_data_completed('send', health_server_request.data_completed_map)
@exception_handler
def report_generate_send():
    if len(request.files) > 1:
        logger_manager.logger.info(
            ({"error_message": "post too many files at once"}, 402))
        return {"error_message": "post too many files at once"}, 402
    elif len(request.files) == 0:
        logger_manager.logger.info(
            ({"error_message": "no post file in this request"}, 402))
        return {"error_message": "no post file in this request"}, 402
    if not health_server_request.check_file_endswith(request.files['zip_file'].filename, '.zip'):
        logger_manager.logger.info(
            ({"error_message": "data is not zip file"}, 402))
        return {"error_message": "data is not zip file"}, 402
    report_table_index = request.form['report_table_index']
    report_table_index_created = health_server_request.query_data_primary_key(
        report_table_index)
    if not report_table_index_created:
        logger_manager.logger.info(
            ({"error_message": "have a didn't create report_table_index"}, 405))
        return {"error_message": "have a didn't create report_table_index"}, 405
    health_server_request.update_data_generate_status(
        report_table_index, 'in_send')
    zip_path = os.path.join(ZIP_FILE_PATH_HEALTH_SERVER,
                            'report_table_index_{}'.format(report_table_index))
    health_server_request.make_dir(zip_path)
    request.files['zip_file'].save(os.path.join(
        zip_path, request.files['zip_file'].filename))
    file_table_data = {
        'report_table_index': report_table_index,
        'zip_path': zip_path,
        'zip_filename': request.files['zip_file'].filename
    }
    health_server_request.create_file(file_table_data)
    health_server_request.update_data_generate_status(
        report_table_index, 'in_send_done')
    logger_manager.logger.info('{} {} {}'.format(
        'send', report_table_index, {"sucess_message": {"result": True}}))
    return {"sucess_message": {"result": True}}


@main.route('/api/report/generate/update', methods=['POST'])
@verify_report_server_token
@check_data_completed('update', health_server_request.data_completed_map)
@exception_handler
def report_generate_update():
    data = request.get_json()
    report_table_index = data['report_table_index']
    health_server_request.update_data_generate_status(
        report_table_index, 'in_update')
    report_table_index_created = health_server_request.query_data_primary_key(
        report_table_index)
    if not report_table_index_created:
        logger_manager.logger.info(
            ({"error_message": "have a didn't create report_table_index"}, 405))
        return {"error_message": "have a didn't create report_table_index"}, 405
    if data['end_flag'] == True:
        health_server_request.update_end_flag(
            data['end_flag'], report_table_index)
    health_server_request.update_data_generate_status(
        report_table_index, 'in_update_done')
    logger_manager.logger.info('{} {} {}'.format(
        'update', report_table_index, {"sucess_message": {"result": True}}))
    return {"sucess_message": {"result": True}}


@main.route('/api/report/generate/query/<report_table_index>', methods=['GET'])
@verify_report_server_token
@exception_handler
def report_generate_query(report_table_index):
    report_table_index_created = health_server_request.query_data_primary_key(
        report_table_index)
    if not report_table_index_created:
        logger_manager.logger.info(
            ({"error_message": "have a didn't create report_table_index"}, 402))
        return {"error_message": "have a didn't create report_table_index"}, 402
    logger_manager.logger.info('{} {} {}'.format(
        'query', report_table_index, health_server_request.query_generate_status(report_table_index)))
    return health_server_request.query_generate_status(report_table_index)


@main.route('/api/report/generate/pdf/<report_table_index>', methods=['GET'])
@verify_report_server_token
@exception_handler
def report_generate_pdf(report_table_index):
    report_table_index_created = health_server_request.query_data_primary_key(
        report_table_index)
    if not report_table_index_created:
        logger_manager.logger.info(
            ({"error_message": "have a didn't create report_table_index"}, 402))
        return {"error_message": "have a didn't create report_table_index"}, 402
    if not health_server_request.query_pdf_path(report_table_index):
        logger_manager.logger.info(
            ({"error_message": "pdf file was not done"}, 403))
        return {"error_message": "pdf file was not done"}, 403
    logger_manager.logger.info('{} {} {}'.format(
        'pdf', report_table_index, {"sucess_message": {"result": True}}))
    return send_file(os.path.join(os.getenv('ROOT_PATH'), health_server_request.query_pdf_path(report_table_index)), mimetype='pdf')
