import os
from flask import Blueprint, request, jsonify, send_file
from utility.wrapper.model import check_ip_adress
from .model import ReportContent
main = Blueprint('report', __name__)

@main.route('/api/report', methods=['GET'])
@check_ip_adress
def get_report_detail():
    res_data = []
    report_id = request.args.get('id', type=str)
    res = ReportContent.query_report_by_id(report_id)
    timestamp_dict = res.algorithm_input
    del timestamp_dict['user_info']
    res_data.append({
        'id' : res.record_id,
        'timestamp_dict': timestamp_dict
    })
    return jsonify(status=True, data=res_data, code=200), 200

@main.route('/api/report/all', methods=['GET'])
@check_ip_adress
def get_report_all():
    res_data = []
    res = ReportContent.get_all()
    for i in res:
        zip_file_list = []
        query_list = ReportContent.query_file_by_report_id(i.record_id)
        if query_list:
            for k in query_list:
                zip_file_list.append(os.path.join(k.zip_path, k.zip_filename))
        units_transfer =  lambda x: "Imperial" if x=="inch" else "Metric"
        locale_transfer = lambda x: "EN" if x=="en" else "TC"
        res_data.append({
            'id': i.record_id,
            'uuid': i.user_id,
            'name': i.user_info['name'],
            'report_code':i.report_code,
            'code_name': i.user_info['name'],
            'timezone': 8,
            'units': units_transfer(i.units),
            'locale': locale_transfer(i.locale),
            'gender': i.user_info['gender'],
            'height': i.user_info['height'],
            'weight': i.user_info['weight'],
            'age': i.user_info['age'],
            'email': i.user_info['email'],
            'phone': 0,
            'birthday': i.user_info['birthday'],
            'zip_file': len(zip_file_list)
        })
    return jsonify(status=True, data=res_data, code=200), 200




@main.route('/api/report/zip_file', methods=['GET'])
@check_ip_adress
def get_report_zip_file():
    res_data = []
    zip_filename = os.path.join(os.getcwd(),'download.zip')
    report_id = request.args.get('id', type=str)
    query_list = ReportContent.query_file_by_report_id(report_id)
    file_list = [os.path.join(i.zip_path, i.zip_filename) for i in query_list]
    ReportContent.compress_all_file(zip_filename, file_list)
    return send_file(zip_filename, attachment_filename=os.path.basename(zip_filename), as_attachment=True)