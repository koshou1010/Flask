import os
ROOT_PATH = '/app'
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", 'log')
ZIP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", 'zip_file')
ZIP_FILE_PATH_HEALTH_SERVER = os.path.join('./','zip_file', 'health_server')
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", 'json_file')
JSON_FILE_PATH_GENERATE_PDF_REQUEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", 'json_file', 'generate_pdf_request')
USER_PDF_PATH = os.path.join('./', 'user_pdf')
E001V1_FILES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", 'user_pdf', 'E001V1Files')
F001V1_FILES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", 'user_pdf', 'F001V1Files')
PDF_A002V2_PATH = os.path.join(USER_PDF_PATH, 'A002V2')
PDF_S001V1_PATH = os.path.join(USER_PDF_PATH, 'S001V1')
PDF_E001V1_PATH = os.path.join(USER_PDF_PATH, 'E001V1')
PDF_F001V1_PATH = os.path.join(USER_PDF_PATH, 'F001V1')
PDF_ZIP_PATH = os.path.join(USER_PDF_PATH, 'zip')

FOLDER_CONTROLLER_LIST = [
    LOG_PATH, 
    ZIP_FILE, 
    ZIP_FILE_PATH_HEALTH_SERVER, 
    USER_PDF_PATH, 
    E001V1_FILES_PATH, 
    PDF_A002V2_PATH, 
    PDF_S001V1_PATH, 
    PDF_E001V1_PATH,
    JSON_FILE,
    JSON_FILE_PATH_GENERATE_PDF_REQUEST,
    PDF_F001V1_PATH,
    PDF_ZIP_PATH,
    F001V1_FILES_PATH
    
    ]


LOCALE_TRANSFER_DICT = {
    "mm" : "Metric",
    "inch" : "Imperial",
    "tw" : "TC",
    "en" : "EN"
}