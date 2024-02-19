from model.token import Token
from utility.sql_alchemy.globals import sqlAlchemy_manager
import datetime


class TokenContent:
    def __init__(self) -> None:
        pass
    
    
    def get_token_identify(self, token: str) -> str:
        with sqlAlchemy_manager.Session() as session:
            res = session.query(Token.customer).filter_by(token=token,
                                                    valid_flag=True
            ).first()
            session.commit()
        return res.customer
    
    def create_token(self, data: dict):
        if 'expire_days' not in data.keys():
            data['expire_days'] = 30
        with sqlAlchemy_manager.Session() as session:
            insert_data = Token(
                token = data['token'],
                customer = data['customer'],
                create_user = data['create_user'],
                update_user = data['update_user'],
                expire_datetime = datetime.datetime.now() + datetime.timedelta(data['expire_days'])
            )
            session.add(insert_data)
            session.commit()
            
    def delete_token(self, data: dict):
        with sqlAlchemy_manager.Session() as session:
            session.query(Token).filter_by(customer=data['customer'],
                                           valid_flag=True).update({Token.valid_flag: False})
            session.commit()


    