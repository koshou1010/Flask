import traceback
from flask import Blueprint, request, send_from_directory, send_file
from .model import GeneratePDFRequestContent
from utility.logger.globals import logger_manager
import os
import sys
import zipfile
import datetime
from application.setting import JSON_FILE_PATH_GENERATE_PDF_REQUEST
from utility.websocket.globals import websocket_manager
from threading import Thread
from application.setting import PDF_ZIP_PATH
from utility.wrapper.model import check_ip_adress
main = Blueprint('generate_pdf_request', __name__)
generate_pdf_request = GeneratePDFRequestContent()


@main.route('/api/pdf/send', methods=['POST'])
@check_ip_adress
def send():

    if not generate_pdf_request.check_file_endswith(request.files['json_file'].filename, '.json'):
        return {"error_message": "json_file is not json file"}, 402

    id = generate_pdf_request.create_data()
    json_path = os.path.join(
        JSON_FILE_PATH_GENERATE_PDF_REQUEST, 'generate_pdf_request_{}'.format(id))
    generate_pdf_request.make_dir(json_path)
    json_file_path = os.path.join(
        json_path, request.files['json_file'].filename)
    request.files['json_file'].save(json_file_path)
    poincare_file_path = None
    if 'poincare_file' in request.files.keys():
        if not generate_pdf_request.check_file_endswith(request.files['poincare_file'].filename, '.jpg'):
            return {"error_message": "poincare_file is not jpg file"}, 402
        poincare_path = os.path.join(
            JSON_FILE_PATH_GENERATE_PDF_REQUEST, 'generate_pdf_request_{}'.format(id))
        poincare_file_path = os.path.join(
            poincare_path, request.files['poincare_file'].filename)
        request.files['poincare_file'].save(poincare_file_path)

    generate_pdf_request.update_json_path_and_poincare_path(
        id, json_file_path, poincare_file_path)
    return {
        "status": True,
        "message": "success",
        "data": {
            "id": id
        }
    }


@main.route('/api/pdf/generate', methods=['POST'])
@check_ip_adress
def generate_pdf():
    data = request.get_json()
    json_path, poincare_path = generate_pdf_request.query_json_path_and_poincare_path(data['id'])
    print(json_path)
    try:
        filename = generate_pdf_request.start_pdf(data, json_path, poincare_path)
    except Exception as e:
        cl, exc, tb = sys.exc_info()
        for line in traceback.extract_tb(tb):
            print('Exception ---> {}'.format(str(line)))
        return {
            "status":False,
            "path":'Exception ---> {}'.format(str(line)),
            "message" : str(e)
        }
    pdf_path = generate_pdf_request.query_pdf_path(data['id'])
    return {"status": True}, 200


@main.route('/api/pdf/download', methods=['POST'])
@check_ip_adress
def download_pdf():
    data = request.get_json()
    pdf_path = generate_pdf_request.query_pdf_path(data['id'])
    return send_file(pdf_path)


@main.route('/api/pdf/send_multiple', methods=['POST'])
def send_multiple():
    print(request.files)
    if not generate_pdf_request.check_file_endswith(request.files['json_file'].filename, '.json'):
        logger_manager.logger.info(
            ({"error_message": "data is not a json file"}, 402))
        return {"error_message": "data is not json file"}, 402
    id = generate_pdf_request.create_data()
    json_path = os.path.join(
        JSON_FILE_PATH_GENERATE_PDF_REQUEST, 'generate_pdf_request_{}'.format(id))
    generate_pdf_request.make_dir(json_path)
    json_file_path = os.path.join(
        json_path, request.files['json_file'].filename)
    request.files['json_file'].save(json_file_path)
    generate_pdf_request.update_json_path(id, json_file_path)
    return {
        "status": True,
        "message": "success",
        "data": {
            "id": id
        }
    }


@main.route('/api/pdf/generate_multiple', methods=['POST'])
def generate_pdf_multiple():
    data = request.get_json()
    task_num = len(data['id'])
    for i in range(task_num):
        json_path = generate_pdf_request.query_json_path(data['id'][i])
        user_id = json_path.split(
            '_')[-1].split('.json')[0].replace('(', '_').replace(')', '').split('_')[-1]
        data['user_id'] = user_id
        filename = generate_pdf_request.start_pdf(data, json_path)

    return {
        "status": True,
        "message": "success"
    }


@main.route('/api/pdf/golden_sample', methods=['GET'])
def report_generate_pdf():
    algo_version = request.args.get('algo_version', type=str)
    if not algo_version:
        return {"status": False, "message": "args error"}, 401
    query_list = generate_pdf_request.query_assign_algo_version_report_progress(
        algo_version)
    zip_filename = os.path.join(PDF_ZIP_PATH, '{}_{}.zip'.format(
        datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), algo_version))
    res = generate_pdf_request.compress_all_pdf(
        zip_filename, query_list, algo_version)
    if not res:
        return {"status": False, "message": "there are many report didnt done"}, 401
    return send_file(os.path.join(os.getenv('ROOT_PATH'),zip_filename), attachment_filename=os.path.basename(zip_filename), as_attachment=True)


@websocket_manager.WebSocketIO.on('connect')
def test_connect():
    print('Client connected')


@websocket_manager.WebSocketIO.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@websocket_manager.WebSocketIO.on('message')
def handle_message(message):
    print('received message: ' + message)

