import os, zipfile
from datetime import date
from utility.google_drive.model import GoogleDriveBackUpController, backup_logger_message
from utility.logger.model import BackUpLogger
from utility.sql_alchemy.globals import sqlAlchemy_manager
from model.backup import BackUp

MONGODB_BACKUP_PATH = './utility/mongodb_/backup'
MONGODB_BACKUP_NAME = 'historydb.zip'
MYSQL_BACKUP_PATH = './utility/mysql_/backup'
MYSQL_BACKUP_NAME = 'report_db.sql.gz'

BACK_UP_MAP = {
    'mysql' :{
        'path' : MYSQL_BACKUP_PATH,
        'name' : MYSQL_BACKUP_NAME
    },
    'mongodb' :{
        'path' : MONGODB_BACKUP_PATH,
        'name' : MONGODB_BACKUP_NAME
    }
}

class DataBaseInit:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    MONGO_DATABASE_URI = os.getenv('MONGO_DATABASE_URI')
    MONGO_DATABASE_NAME = os.getenv('MONGO_DATABASE_NAME')
    MONGO_DATABASE_COLLECTION = os.getenv('MONGO_DATABASE_COLLECTION')
    
    def __init__(self) -> None:
        self.mysql_connect()
        self.mongo_connect()
        
    def mysql_connect(self):
        from utility.sql_alchemy import setup
        setup(self.SQLALCHEMY_DATABASE_URI)
    
    def mongo_connect(self):
        from utility.mongodb_ import setup
        setup(host=self.MONGO_DATABASE_URI, 
              testing=False,
              db_name= self.MONGO_DATABASE_NAME,
              collection=self.MONGO_DATABASE_COLLECTION
              )

def create_backup_data(file_path: str, type: str):
    with sqlAlchemy_manager.Session() as session:
        insert_data = BackUp(
            file_path = file_path,
            back_up_flag = False,
            type = type
        )
        session.add(insert_data)
        session.commit()
        
def update_backup_flag(id: int):
    with sqlAlchemy_manager.Session() as session:
        session.query(BackUp).filter_by(id=id).update({BackUp.back_up_flag : True})
        session.commit()
        session.close()


def rename(db : str):
    today = date.today()
    print(os.listdir(BACK_UP_MAP[db]['path']))
    if BACK_UP_MAP[db]['name'] in os.listdir(BACK_UP_MAP[db]['path']):
        old_name = os.path.join(BACK_UP_MAP[db]['path'],  BACK_UP_MAP[db]['name'])
        new_name = os.path.join(BACK_UP_MAP[db]['path'], '{}_{}'.format(today,  BACK_UP_MAP[db]['name']))
        os.rename(old_name, new_name)
        return new_name


        
def check_local_file():
    google_drive_backup = GoogleDriveBackUpController()
    
    # backup mongo
    new_name = rename('mongodb')
    create_backup_data(new_name, 'mongodb') 
    not_backup_files = google_drive_backup.query_not_backup_files('mongodb')
    if not_backup_files:
        for file in not_backup_files:
            google_drive_backup.upload(file.file_path, 'mongodb')  
            update_backup_flag(file.id)

    # backup mysql
    new_name = rename('mysql')
    create_backup_data(new_name, 'mysql') 
    not_backup_files = google_drive_backup.query_not_backup_files('mysql')
    if not_backup_files:
        for file in not_backup_files:
            google_drive_backup.upload(file.file_path, 'mysql')  
            update_backup_flag(file.id)
             
    # backup pdf
    pdf_type_list = ['S001V1', 'E001V1', 'A002V2']
    for type in pdf_type_list:
        not_backup_files = google_drive_backup.query_not_backup_files(type)
        if not_backup_files:
            for file in not_backup_files:
                google_drive_backup.upload(file.file_path, type)  
                update_backup_flag(file.id)       

def zip_mongo_backup():
    os.chdir(MONGODB_BACKUP_PATH)
    zf = zipfile.ZipFile('{}.zip'.format('historydb'), 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk('historydb'):
        for file_name in files:
            zf.write(os.path.join(root,file_name))

if __name__ == '__main__':
    backup_logger_message('Start Backup ... ')
    DataBaseInit()
    zip_mongo_backup()
    os.chdir('/home/koshou/FWA10_Report_Server')
    check_local_file()
    backup_logger_message('End Backup ... ')
    