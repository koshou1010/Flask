from testing.base import BaseTestCase
from testing.func import mock_access_token
from utility.algorithms.report.ExerciseReportGenerator import ExerciseReportGenerator
from utility.algorithms.report.SleepQualityReportGenerator import SleepQualityReportGenerator
from utility.algorithms.report.CardiovascularHealthReportGenerator import CardiovascularHealthReportGenerator
from datetime import datetime
import time

token = mock_access_token()

class AlgorithmInterface:
    def __init__(self, zip_path):

        self.zip_path = zip_path
        self.algorithm_setting_map = {
            'S001V1' : {'time_format' : '%Y%m%d %H%M%S'},
            'E001V1' : {'time_format' : '%Y%m%d %H%M%S'},
            'A002V2' : {'time_format' : '%Y%m%d'}
        }
        
        self.template_dict  = {
            "start_time" :0,
            "end_time" : 0,
            "cost_time" : 0
        }
    def transfer_timestamp(self, algorithm_input : dict, time_format : str):
        for key in algorithm_input.keys():
            if key.endswith('_tt'):
                algorithm_input[key] = datetime.fromtimestamp(algorithm_input[key]/1000).strftime(time_format)
        return algorithm_input
    
    def replace_time(self)->dict:
        for key in self.template_dict.keys():
            if key == "cost_time":
                self.template_dict[key] = "{}m{}s".format(self.template_dict[key]//60, self.template_dict[key]%60)
            else:
                self.template_dict[key] = str(datetime.fromtimestamp(self.template_dict[key]))
        self.template_dict['status'] = True
        return self.template_dict
    
    def assign_locale_units_timezone(self, user_info:dict):
        from application.setting import LOCALE_TRANSFER_DICT
        if user_info['locale'] not in LOCALE_TRANSFER_DICT.keys():
            user_info['language'] = LOCALE_TRANSFER_DICT['tw']
        else:
            user_info['language'] = LOCALE_TRANSFER_DICT[user_info['locale']]
        if user_info['units'] not in LOCALE_TRANSFER_DICT.keys():
            user_info['unit'] = LOCALE_TRANSFER_DICT['mm']
        else:
            user_info['unit'] = LOCALE_TRANSFER_DICT[user_info['units']]
        
    def s001v1(self)->dict:
        try:
            self.template_dict['start_time'] = int(time.time())
            exercise_instanse = ExerciseReportGenerator(self.zip_path)
            algorithm_input = {
                "user_info": 
                    {
                        "id": "925"
                    }, 
                    "exercise_end_tt": 0, 
                    "step_test_end_tt": 0,
                    "exercise_start_tt": 0, 
                    "step_test_start_tt": 0
                    }
            algorithm_input = self.transfer_timestamp(algorithm_input, self.algorithm_setting_map['S001V1']['time_format'])
            self.assign_locale_units_timezone(algorithm_input['user_info'])
            res = exercise_instanse.ExerciseAnalysisReport(algorithm_input['step_test_start_tt'],algorithm_input['step_test_end_tt'],algorithm_input['exercise_start_tt'],algorithm_input['exercise_end_tt'],algorithm_input['user_info'])
            print("HERE_s001v1")
            print(res)
            if res['status']:
                self.template_dict['end_time'] = int(time.time())
                self.template_dict['cost_time'] = self.template_dict['end_time'] - self.template_dict['start_time']
                return self.replace_time()
            else:
                self.template_dict['status'] = False
                return self.template_dict
        except:
            self.template_dict['status'] = False
            return self.template_dict
            
    def e001v1(self)->dict:
        try:
            self.template_dict['start_tile_ume'] = int(time.time())
            sleep_instanse = SleepQualityReportGenerator(self.zip_path)
            algorithm_input =  {
                "user_info": {
                    "id": "1125"                
                }, 
                "report_end_tt": 0, 
                "report_start_tt": 0
            }
            algorithm_input = self.transfer_timestamp(algorithm_input, self.algorithm_setting_map['E001V1']['time_format'])
            self.assign_locale_units_timezone(algorithm_input['user_info'])
            res = sleep_instanse.SleepAnalysisReport(algorithm_input['report_start_tt'],algorithm_input['report_end_tt'],algorithm_input['user_info'])
            print("HERE_e001v1")
            print(res)
            if res['status']:
                self.template_dict['end_time'] = int(time.time())
                self.template_dict['cost_time'] = self.template_dict['end_time'] - self.template_dict['start_time']
                return self.replace_time()
            else:
                self.template_dict['status'] = False
                return self.template_dict
        except Exception as e:
            print(e)
            self.template_dict['status'] = False
            return self.template_dict
    
    
    def a002v2(self)->dict:
        try:
            self.template_dict['start_time'] = int(time.time())
            seven_instanse = CardiovascularHealthReportGenerator(self.zip_path)
            algorithm_input={
                "user_info": {
                    "id": "986"
                },
                "report_end_tt": 0, 
                "report_start_tt": 0
                }            
            algorithm_input = self.transfer_timestamp(algorithm_input, self.algorithm_setting_map['A002V2']['time_format'])
            self.assign_locale_units_timezone(algorithm_input['user_info'])
            res = seven_instanse.HealthReportGenerator(algorithm_input['report_start_tt'],algorithm_input['report_end_tt'],algorithm_input['user_info'], "A002V2", [])
            print("HERE_a002v2")
            print(res)
            if res['status']:
                self.template_dict['end_time'] = int(time.time())
                self.template_dict['cost_time'] = self.template_dict['end_time'] - self.template_dict['start_time']
                return self.replace_time()
            else:
                self.template_dict['status'] = False
                return self.template_dict
        except:
            self.template_dict['status'] = False
            return self.template_dict

class AlgorithmTestCase(BaseTestCase):
    
    def test_s001V1(self):
        zip_path = './testing/modules/data/sport'
        instance = AlgorithmInterface(zip_path)
        time_dict = instance.s001v1()
        self.assertEqual(time_dict['status'], True)
        
    def test_e001V1(self):
        zip_path = './testing/modules/data/sleep'
        instance = AlgorithmInterface(zip_path)
        time_dict = instance.e001v1()
        self.assertEqual(time_dict['status'], True)
        
    def test_a002V2(self):
        zip_path = './testing/modules/data/seven'
        instance = AlgorithmInterface(zip_path)
        time_dict = instance.a002v2()
        self.assertEqual(time_dict['status'], True)
