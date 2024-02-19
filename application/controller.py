from flask import Blueprint
from application.health_server_request.model import HealthServerReportGenerator
from utility.algorithms.report.version import __version__
from utility.wrapper.model import verify_report_server_token
from utility.sql_alchemy.globals import sqlAlchemy_manager

main = Blueprint('main', __name__)

@main.route('/api/algo_version', methods=['GET'])
@verify_report_server_token
def report_generate_query():
    return {"status":True, "data":__version__}

@main.route('/api/create_db', methods=['GET'])
def create_db():
    sqlAlchemy_manager.create_all()
    return {"status":True}

def start_process(content: dict):
    '''
    Interface of after queue get content, start algorithm and then generate pdf
    '''

    REQUEST_INSTANCE_MAP = {
        'health_server_request': HealthServerReportGenerator()
    }

    REQUEST_INSTANCE_MAP[content['request_type']].start_process_entrance(content)
