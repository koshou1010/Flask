import datetime
import os, random, string, re
import uuid
import hashlib
import time
from utility.request_mapper import base_json_content
from model.user_profile import UserProfile
from utility.sql_alchemy.globals import sqlAlchemy_manager


def password_random_salt_hash(password, randomsalt):
    return f"${randomsalt}${hashlib.sha512(str(os.getenv('SALT')+randomsalt+password).encode('utf-8')).hexdigest()}"


class SignUpContent(base_json_content):

    account: str = ""
    password: str = ""
    hash_password: str = ""
    phone_number: str = ""
    email: str = None
    token: str = ""
    last_login_datetime: str = ""

    def create_user(self):
        randomsalt=''.join(random.sample(string.ascii_letters, 8))
        self.hash_password = password_random_salt_hash(self.password, randomsalt)
        with sqlAlchemy_manager.Session() as session:
            insert_data = UserProfile(
                account=self.account,
                hash_password=self.hash_password,
                create_user=self.account,
                update_user=self.account,
                email=self.email
            )
            session.add(insert_data)
            session.commit()
            session.refresh(insert_data)
        return insert_data.id


class SignInContent(base_json_content):

    account: str = ""
    password: str = ""
    hash_password: str = ""
    phone_number: str = ""
    email: str = ""
    token: str = ""
    last_login_datetime: str = ""
    def query_user_exist(self):
        with sqlAlchemy_manager.Session() as session:
            res = session.query(UserProfile).filter(
                UserProfile.account == self.account,
                UserProfile.valid_flag == True
            ).first()
        return res

    def update_hash_password(self, new_hash_password):
        with sqlAlchemy_manager.Session() as session:
            res = session.query(UserProfile).filter(
                UserProfile.account == self.account,
                UserProfile.valid_flag == True
            ).update({'hash_password': new_hash_password})
            session.commit()

    def check_hash_password_format(self, pwd: str) -> bool:
        new_hash_password_format = '\$\w*\$\w*'
        return re.search(new_hash_password_format, pwd)