import logging
import os, time
import multiprocessing
from logging.handlers import TimedRotatingFileHandler


lock = multiprocessing.Lock()

class RebuildTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super(RebuildTimedRotatingFileHandler, self).__init__(*args, **kwargs)
        self.suffix_time = ""
        self.origin_basename = self.baseFilename

    def shouldRollover(self, record):
        timeTuple = time.localtime()
        if self.suffix_time != time.strftime(self.suffix, timeTuple) or not os.path.exists(self.origin_basename+'.'+self.suffix_time):
            return 1
        else:
            return 0

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTimeTuple = time.localtime()
        self.suffix_time = time.strftime(self.suffix, currentTimeTuple)
        self.baseFilename = self.origin_basename + '.' + self.suffix_time
        self.mode = 'a'
        global lock
        with lock:
            if self.backupCount > 0:
                for s in self.getFilesToDelete():
                    os.remove(s)
        if not self.delay:
            self.stream = self._open()

    def getFilesToDelete(self):
        dirName, baseName = os.path.split(self.origin_basename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result

class Logger(object):

    def __init__(self,
                 filename = './log/report_server_log',
                 level='info',
                 when='D',
                 back_count=0,
                 fmt='[%(asctime)s %(levelname)-3s] %(message)s'):
        self.level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
        }
        self.setup(filename, level, when, back_count, fmt)
    
    def remove_handler(self):
        self.logger.removeHandler(self.console_handler)
        self.logger.removeHandler(self.timer_handler)
        
    def setup(self, filename:str, level:str, when:str, back_count:int, fmt:str):
        self.logger = logging.getLogger()
        format_str = logging.Formatter(fmt)  
        self.logger.setLevel(self.level_relations.get(level))  
        self.console_handler = logging.StreamHandler()  
        self.console_handler.setLevel(logging.DEBUG)
        self.console_handler.setFormatter(format_str)  
        self.timer_handler = RebuildTimedRotatingFileHandler(filename=filename, when=when, backupCount=back_count, encoding='utf-8') 
        self.timer_handler.suffix = "_%Y_%m_%d.txt"
        self.timer_handler.setFormatter(format_str)  
        if not self.logger.hasHandlers():
            self.logger.addHandler(self.console_handler)  
            self.logger.addHandler(self.timer_handler)
        

    
    
class GeneratePDFLogger(Logger):
    def __init__(self):
        super(GeneratePDFLogger,self).__init__(filename = './log/generate_pdf_log')    
    

class BackUpLogger(Logger):
    def __init__(self):
        super(BackUpLogger,self).__init__(filename = './log/backup_log')    
        


