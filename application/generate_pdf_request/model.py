import os, time, json
from application.generate_pdf_interface.model import fake_choose_generate_pdf_version
from application.setting import  E001V1_FILES_PATH, PDF_A002V2_PATH,PDF_S001V1_PATH,PDF_E001V1_PATH, F001V1_FILES_PATH
from utility.sql_alchemy.globals import sqlAlchemy_manager
from model.generate_pdf_request import GeneratePDFRequest
from model.report import Report
import os, zipfile
from application.setting import PDF_ZIP_PATH

S001V1_LOCALE_JSON_PATH = os.path.join(os.getcwd(), 'application', 'reportgen', 'locale', 's001v1.json')
E001V1_LOCALE_JSON_PATH = os.path.join(os.getcwd(), 'application', 'reportgen', 'locale', 'e001v1.json')
A002V2_LOCALE_JSON_PATH = os.path.join(os.getcwd(), 'application', 'reportgen', 'locale', 'a002v2.json')


class GeneratePDFRequestContent:
    def __init__(self) -> None:
        pass
    
    def create_data(self) -> int:
        with sqlAlchemy_manager.Session() as session:
            data = GeneratePDFRequest()
            session.add(data)
            session.commit()
            pk = data.id
        return pk
    
    
    def query_json_path_and_poincare_path(self, id:int) -> str:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(GeneratePDFRequest.json_path, GeneratePDFRequest.poincare_path).filter_by(id=id).first()
            session.commit()
        return query_result
    
    def update_json_path_and_poincare_path(self, id, json_path, poincare_path):
        with sqlAlchemy_manager.Session() as session:
            session.query(GeneratePDFRequest).filter_by(id=id).update({
                GeneratePDFRequest.json_path: json_path,
                GeneratePDFRequest.poincare_path: poincare_path,
            })
            session.commit()
            
    def query_pdf_path(self, id : int) -> str:
        with sqlAlchemy_manager.Session() as session:
            query_result = session.query(GeneratePDFRequest).get(id).pdf_path
            session.commit()
        return query_result
    
    def update_pdf_path(self, id, path):
        with sqlAlchemy_manager.Session() as session:
            session.query(GeneratePDFRequest).filter_by(id=id).update({GeneratePDFRequest.pdf_path: path})
            session.commit()

    
    def query_assign_algo_version_report_progress(self, algo_version: str):
        '''
        query all assign golden sample,
        check there are all done or not 
        '''
        
        with sqlAlchemy_manager.Session() as session:
            query = session.query(Report.record_id, Report.result_message, Report.pdf_path).filter(
                Report.golden_sample==True,
                Report.end_flag==True,
                Report.algo_version==algo_version                                                   
            ).all()
            session.commit()
        return query
    
    def compress_all_pdf(self, zip_filename: str, query_list: list, algo_version: str) -> bool:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i in query_list:
                if not i.result_message or not i.pdf_path:
                    return False
                zf.write(i.pdf_path, os.path.join(algo_version, os.path.basename(i.pdf_path)))   
        return True

    
    def check_file_endswith(self, file : str, kind : str) -> bool:
        return file.endswith(kind)
    
    def make_dir(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
            
    def download_json_file(self):
        pass
    

    def start_pdf(self, data, json_path, poincare_path):
        self.locale = "tw"
        report_code = data['report_code']
        self.filename = '{0}_{1:05d}_{2}.pdf'.format(report_code, int(data['user_id']), str(int(time.time())))
        print('json_output_path: {}'.format(json_path))
        print('Start {} PDF'.format(report_code))
        generate_pdf_version_instanse = fake_choose_generate_pdf_version(report_code)
        if report_code == 'S001V1':
            with open(json_path, 'r', encoding='utf-8') as f:
                report_json = json.load(f)
            with open(S001V1_LOCALE_JSON_PATH, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            locale_data_selected = locale_data[self.locale]
            pdf_path = generate_pdf_version_instanse.genReport(report_json, self.filename, '', locale=self.locale, locale_data=locale_data_selected)
            
        elif report_code == 'E001V1':
            with open(json_path, 'r', encoding='utf-8') as f:
                report_json = json.load(f)
            with open(E001V1_LOCALE_JSON_PATH, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            locale_data_selected = locale_data[self.locale]
            self.temp_png_path = os.path.join(E001V1_FILES_PATH, str(data['user_id']))
            if not os.path.exists(self.temp_png_path):
                os.mkdir(self.temp_png_path)
            pdf_path = generate_pdf_version_instanse.genReport(report_json, self.filename, self.temp_png_path, locale=self.locale, locale_data=locale_data_selected)
        
        elif report_code == 'F001V1':
            with open(json_path, 'r', encoding='utf-8') as f:
                report_json_string = f.read()
            report_json = json.loads(json.dumps(eval(report_json_string)))
            self.temp_png_path = os.path.join(F001V1_FILES_PATH, str(data['user_id']))
            if not os.path.exists(self.temp_png_path):
                os.mkdir(self.temp_png_path)
            pdf_path = generate_pdf_version_instanse.genReport(report_json, self.filename, self.temp_png_path)
        
        elif report_code == 'A002V2':
            with open(json_path, 'r', encoding='utf-8') as f:
                report_json = json.load(f)
            with open(A002V2_LOCALE_JSON_PATH, 'r', encoding='utf-8') as f:
                locale_data = json.load(f)
            locale_data_selected = locale_data[self.locale]
            pdf_path = generate_pdf_version_instanse.genReport(report_json, self.filename, assign_poincare_path=poincare_path, locale=self.locale, locale_data=locale_data_selected)
            
        print('End {} PDF.'.format(report_code))
        self.update_pdf_path(data['id'], pdf_path)
        return self.filename
        

