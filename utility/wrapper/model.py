import os
import socket
from flask import request, jsonify
# from torch import is_conj
from utility.sql_alchemy.globals import sqlAlchemy_manager
from model.token import Token
from utility.logger.globals import logger_manager


def verify_report_server_token(func):
    def wrapper(*args, **kwargs):
        try:
            token_type, access_token = request.headers.get(
                'Authorization').split(' ')
        except:
            logger_manager.logger.info(({'error': 'please verify token'}, 401))
            return {'error': 'please verify token'}, 401
        try:
            with sqlAlchemy_manager.Session() as session:
                res = session.query(Token).filter_by(
                    token=str(access_token)).all()
                session.commit()
        except Exception as e:
            logger_manager.logger.info(
                ({'error': 'Mysql sleep please request again'}, 501))
            logger_manager.logger.info(
                'Exception ---> function : {}, {}'.format(func.__name__, e))
            return {'error': 'Mysql sleep please request again'}, 501
        if token_type != 'Bearer':
            logger_manager.logger.info(({'error': 'token type error'}, 401))
            return {'error': 'token type error'}, 401
        if not res:
            logger_manager.logger.info(({'error': 'access token error'}, 401))
            return {'error': 'access token error'}, 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper



def verify_token_identify(identify: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                token_type, access_token = request.headers.get('Authorization').split(' ')
            except:
                logger_manager.logger.info(({'error': 'please verify token'}, 401))
                return {'error': 'please verify token'}, 401
            try:
                with sqlAlchemy_manager.Session() as session:
                    res = session.query(Token.token).filter_by(customer=identify,
                                                         valid_flag=True
                    ).first()
                    session.commit()
            except Exception as e:
                logger_manager.logger.info(
                    'Exception ---> function : {}, {}'.format(func.__name__, e))
                return {'error': 'Mysql request failed'}, 501
            if token_type != 'Bearer':
                logger_manager.logger.info(({'error': 'token type error'}, 401))
                return {'error': 'token type error'}, 401
            if not res:
                logger_manager.logger.info(({'error': 'access token error'}, 401))
                return {'error': 'access token error'}, 401
            if res.token != access_token:
                logger_manager.logger.info(({'error': 'access token error'}, 401))
                return {'error': 'access token error'}, 401
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

def check_data_completed(post_api_mode, map):
    def decorator(func):
        def wrapper2(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form
            if post_api_mode == 'create':
                if 'golden_sample' not in data.keys():  
                    data['golden_sample'] = False
            for key in data.keys():
                if key not in map[post_api_mode]:
                    logger_manager.logger.info(
                        ({"error_message": "unknow data : {}".format(key)}, 402))
                    return {"error_message": "unknow data : {}".format(key)}, 402
            for key in map[post_api_mode]:
                if key not in list(data.keys()):
                    logger_manager.logger.info(
                        ({"error_message": "missing data : {}".format(key)}, 402))
                    return {"error_message": "missing data : {}".format(key)}, 402
            return func(*args, **kwargs)
        wrapper2.__name__ = func.__name__
        return wrapper2
    return decorator


def exception_handler(func):
    def wrapper3(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger_manager.logger.info(
                'Exception ---> function : {}, {}'.format(func.__name__, e))
            return {"error_message": str(e)}, 505
        return result
    wrapper3.__name__ = func.__name__
    return wrapper3


def check_ip_adress(func):
    def wrapper2(*args, **kwargs):
        if os.getenv('MODE') in ['develop', 'release']:
            ip = request.access_route[0]
            if socket.gethostbyname(os.getenv('DDNS_URL')) != ip:
                return jsonify(status=False, message="Identify Error", code=401.6), 401
        return func(*args, **kwargs)
    wrapper2.__name__ = func.__name__
    return wrapper2
