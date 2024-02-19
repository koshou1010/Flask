
from flask import Blueprint, request, jsonify
from .model import SignUpContent, SignInContent, password_random_salt_hash
from utility.wrapper.model import check_ip_adress
from utility.request_mapper import request_json_mapping
from sqlalchemy.exc import IntegrityError
from utility.exception_handler.mysql_handler import MySQLExceptionHandler
import random, string, re


main = Blueprint('login', __name__)


@main.route('/api/signin', methods=['POST'])
@request_json_mapping(SignInContent)
@check_ip_adress
def sign_in(request_content: SignInContent): 
    res_data = {}
    res = request_content.query_user_exist()
    if not res: 
        return jsonify({"msg": "Username Failed"}), 401
    if not request_content.check_hash_password_format(res.hash_password):
        randomsalt=''.join(random.sample(string.ascii_letters, 8))
        request_content.update_hash_password(password_random_salt_hash(request_content.password, randomsalt))
    else:
        personal_salt = re.match('\$\w*',res.hash_password).group().split('$')[-1]
        if password_random_salt_hash(request_content.password, personal_salt) != res.hash_password:
            return jsonify({"msg": "Password Failed"}), 401
    res_data['token'] = res.token
    return jsonify(status=True, data=res_data, code=200), 200
    
@main.route('/api/signup', methods=['POST'])
@request_json_mapping(SignUpContent)
@check_ip_adress
def signup(request_content: SignUpContent):
    # print(request.get_json())
    try:
        if 'koshou.com' not in request.get_json()['email']:
            return jsonify(status=False), 500
        id = request_content.create_user()
    except IntegrityError as e:
        return MySQLExceptionHandler.uk_write_error(e)
    except Exception as e:
        print(e)
        return jsonify(status=False), 500
    return jsonify(status=True, data={"id" :id}, code=200), 200

