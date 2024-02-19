import os, sys, traceback
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from utility.logger.model import BackUpLogger
from utility.sql_alchemy.globals import sqlAlchemy_manager
from model.backup import BackUp
from dotenv import load_dotenv
load_dotenv("./config/.env")

FOLDER_ID_MAP = {
    "A002V2" : os.getenv('A002V2_FOLDER'),
    "S001V1" : os.getenv('S001V1_FOLDER'),
    "E001V1" : os.getenv('E001V1_FOLDER'),
    'mysql' : os.getenv('MYSQL_FOLDER'),
    'mongodb' : os.getenv('MONGODB_FOLDER'),
}

logger_con = BackUpLogger()
def backup_logger_message(message):
    logger_con.logger.info(message) 
    
class GoogleDriveBackUpController:
    def __init__(self):
        gauth = GoogleAuth(settings_file = os.path.join(os.path.dirname(__file__), 'settings.yaml'))
        gauth.CommandLineAuth() 
        self.drive = GoogleDrive(gauth)


    def check_on_gdrive(self, filename : str, folder :str) -> bool:
        file_list = self.drive.ListFile({'q': '"{}" in parents and trashed=false'.format(FOLDER_ID_MAP[folder])}).GetList()
        for file in file_list:
            if file['title'] == filename:
                return True
        return False
    
    def query_not_backup_files(self, type: str) -> list:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(BackUp.id, BackUp.file_path).filter_by(back_up_flag=False,
                                                           type=type).all()
            session.commit()
        return query_result


    
    def upload(self, file_path : str, folder : str):
        try:
            filename = file_path.split('/')[-1]
            # floder = filename.split('_')[0]  
            upload_file = self.drive.CreateFile({"title":filename,
                                    'mimeType': 'application/pdf',
                                    "parents": [{"kind": "drive#fileLink", "id": "{}".format(FOLDER_ID_MAP[folder])}]})
            upload_file.SetContentFile(file_path)
            if not self.check_on_gdrive(filename, folder):
                upload_file.Upload() 
                backup_logger_message("Uploading succeeded!")
            else:
                backup_logger_message("it was in google drive")
        except Exception as e:
            backup_logger_message("Uploading failed.")
            cl, exc, tb = sys.exc_info()
            for line in traceback.extract_tb(tb):
                backup_logger_message('Exception ---> {}'.format(str(line)))
            backup_logger_message(e)



                

