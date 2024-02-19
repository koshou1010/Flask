import json
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


class MailCenter:

    def __init__(self, host: str, port: int, user_name: str, user_password: str, code_name : str,exception_recipient: str, failed_recipient:str, email_alias: str):

        # SMTP Settings.
        self.Host = host
        self.Port = port

        # SMTP Connection Account Settings.
        self.code_name = code_name
        self.UserName = user_name
        self.Password = user_password
        self.exception_recipient = exception_recipient
        self.failed_recipient = failed_recipient
        self.email_alias = email_alias

    def send_email(self, subject, msg_paramters: dict, type = "exception"):
        exception_content_template = '''
        <p>Hi all</p>
        <span>有一筆報告產生時發生例外</span>
        <div >
            <span>例外類別:</span>
            <span style="color:red">{}_exception</span>
        </div>
        <div >
            <span>報告類別:</span>
            <span style="color:red">{}</span>
        </div>
        <div >
            <span>parameters:</span>
            <span style="color:red">{}</span>
        </div>
        <div>
            <span>失敗訊息:</span>
            <span style="color:red">{}</span>
        </div>
        '''.format(msg_paramters['type'], msg_paramters['report_code'], msg_paramters['algorithm_input'], msg_paramters['message'])

        exception_file_large_content_template = '''
        <p>Hi all</p>
        <span>有一筆報告產生時發生例外</span>
        <div >
            <span>例外類別:</span>
            <span style="color:red">{}_exception</span>
        </div>
        <div >
            <span>報告類別:</span>
            <span style="color:red">{}</span>
        </div>
        <div >
            <span>parameters:</span>
            <span style="color:red">{}</span>
        </div>
        <div>
            <span>失敗訊息:</span>
            <span style="color:red">{}</span>
        </div>
        <div>
            <p> </p>
            <span style="color:red">檔案過大, 請聯絡Koshou拿檔案</span>
        </div>
        '''.format(msg_paramters['type'], msg_paramters['report_code'], msg_paramters['algorithm_input'], msg_paramters['message'])
        failed_content_template = '''
        <p>Hi all</p>
        <span>有一筆報告產生失敗</span>
        <div >
            <span>報告類別:</span>
            <span style="color:red">{}</span>
        </div>
        <div >
            <span>parameters:</span>
            <span style="color:red">{}</span>
        </div>
        <div>
            <span>失敗訊息:</span>
            <span style="color:red">{}</span>
        </div>
        '''.format(msg_paramters['report_code'], msg_paramters['algorithm_input'], msg_paramters['message'])
        msg = MIMEMultipart()
        # msg = MIMEText(content_template, 'html', 'utf-8')  # 郵件內文
        if type == "exception":
            file_success = self.check_file_size(msg_paramters['all_file_list'])
            msg['To'] = self.exception_recipient  # 收件人 email
            if file_success:
                msg.attach(MIMEText(exception_content_template, 'html', 'utf-8'))  # 郵件內文
                for file in msg_paramters['all_file_list']:
                    with open(file, 'rb') as f:
                        file_obj = f.read()
                    attach_file = MIMEApplication(file_obj, Name=os.path.split(file)[-1])    # 設定附加檔案
                    msg.attach(attach_file)                       # 加入附加檔案
            else:
                msg.attach(MIMEText(exception_file_large_content_template,'html', 'utf-8'))  # 郵件內文
        elif type == "failed":
            msg['To'] = self.failed_recipient  # 收件人 email
            msg.attach(MIMEText(failed_content_template,'html', 'utf-8'))  # 郵件內文
        msg['Subject'] = subject           # 郵件標題
        msg['From'] = '{} <{}>'.format(self.code_name, self.email_alias)  # 暱稱或是 email
        smtpObj = smtplib.SMTP(self.Host, self.Port)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(self.UserName, self.Password)
        status = smtpObj.send_message(msg)
        if status == {}:
            print('郵件傳送成功！')
        else:
            print('郵件傳送失敗...')
        smtpObj.quit()

    def check_file_size(self, file_list: list) -> bool:
        file_size_list = []
        for file in file_list:
            file_size_list.append(os.stat(file).st_size / (1024*1024))
        return max(file_size_list) < 25


def send_email(subject, msg: dict, type = "exception"):
    from utility.mail_center import initialize as initialize_mail_center
    mail_center = initialize_mail_center()
    mail_center.send_email(subject, msg, type)
