from .model import MailCenter
from dotenv import load_dotenv
import os

load_dotenv("./config/.env")

def initialize():

    host = os.getenv('HOST')
    port = os.getenv('PORT')
    name = os.getenv('SENDER')
    password = os.getenv('PASSWORD')
    email_alias = os.getenv('SENDER_MAIL_ALIAS')
    code_name = os.getenv('CODENAME')
    exception_recipient = os.getenv('RECIPIENT_EXCEPTION_TYPE')
    failed_recipient = os.getenv('RECIPIENT_FAILED_TYPE')
    
    return MailCenter(
        host=host,
        port=port,
        user_name=name,
        user_password=password,
        code_name = code_name,
        exception_recipient = exception_recipient,
        failed_recipient = failed_recipient,
        email_alias = email_alias
    )
