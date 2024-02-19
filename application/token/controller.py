from flask import request, Blueprint
import socket, os
from utility.wrapper.model import check_ip_adress
from .model import TokenContent
from utility.wrapper.model import verify_token_identify
token_content = TokenContent()
main = Blueprint('token', __name__)


@main.route('/api/token', methods=['GET','POST', 'PUT','DELETE'])
@verify_token_identify('TokenServer')
@check_ip_adress
def get_token():
    token_type, access_token = request.headers.get('Authorization').split(' ')
    data = request.get_json()
    if request.method == "GET":
        customer = request.args.get('customer', type=str)
        return {"status" : True, "message" : customer}
    elif request.method == "POST":
        user = token_content.get_token_identify(access_token)
        data['create_user'] = user
        data['update_user'] = user
        token_content.create_token(data)
    elif request.method == "PUT":
        pass
    elif request.method == "DELETE":
        token_content.delete_token(data)
        
    return {"status":True}

