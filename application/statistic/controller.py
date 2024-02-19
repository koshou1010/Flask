from flask import Blueprint, request, jsonify
from .model import SleepStatisticContent
from utility.wrapper.model import check_ip_adress

main = Blueprint('statistic', __name__)


@main.route('/api/statistic/all', methods=['GET'])
@check_ip_adress
def get_all_sleep_statistic():
    res_data = []
    res = SleepStatisticContent.get_all()
    for i in res:
        report = SleepStatisticContent.query_report_by_report_id(i.report_id)
        res_data.append({
            'id':i.id,
            'report_id': i.report_id,
            'algo_version': report.algo_version,
            'total_sleep_hrs': i.total_sleep_hrs,
            'total_sleep_hrs_without_missing': i.total_sleep_hrs_without_missing,
            'missing_times': i.missing_times,
            'awake_times': i.awake_times,
            'rem_times': i.rem_times,
            'light_times': i.light_times,
            'deep_times': i.deep_times,
            'awake_per_with_awake': i.awake_per_with_awake,
            'rem_per_with_awake': i.rem_per_with_awake,
            'light_per_with_awake': i.light_per_with_awake,
            'deep_per_with_awake': i.deep_per_with_awake,
            'rem_per_without_awake': i.rem_per_without_awake,
            'light_per_without_awake': i.light_per_without_awake,
            'deep_per_without_awake': i.deep_per_without_awake
        })
    return jsonify(status=True, data=res_data, code=200), 200


@main.route('/api/statistic', methods=['GET'])
@check_ip_adress
def get_sleep_statistic_by_report_id():
    report_id = request.args.get('report_id', type=str)
    res_data = []
    query = SleepStatisticContent.query_sleep_statistic_by_report_id(report_id)

    res_data.append({
        'report_id': query.report_id,
        'total_sleep_hrs': query.total_sleep_hrs,
        'total_sleep_hrs_without_missing': query.total_sleep_hrs_without_missing,
        'missing_times': query.missing_times,
        'awake_times': query.awake_times,
        'rem_times': query.rem_times,
        'light_times': query.light_times,
        'deep_times': query.deep_times,
        'awake_per_with_awake': query.awake_per_with_awake,
        'rem_per_with_awake': query.rem_per_with_awake,
        'light_per_with_awake': query.light_per_with_awake,
        'deep_per_with_awake': query.deep_per_with_awake,
        'rem_per_without_awake': query.rem_per_without_awake,
        'light_per_without_awake': query.light_per_without_awake,
        'deep_per_without_awake': query.deep_per_without_awake
    })
    return jsonify(status=True, data=res_data, code=200), 200
