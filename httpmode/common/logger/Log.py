import sys
sys.path.append('..')


from datetime import datetime
import pytz

from logging import handlers
import logging

class Logger():
    level_relations={
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'critical':logging.CRITICAL
    }
    def __init__(self,
                 filename,
                 level='info',
                 when='D',
                 back_count=3,
                 fmt='%(asctime)s  -  [line:%(lineno)d]  -  %(levelname)s: %(message)s'):
        self.logger=logging.getLogger(filename)
        format_str=logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        th=handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=back_count,encoding='utf-8')
        th.setFormatter(format_str)
        
        

def log(msg,withTime=True):
    timestamp=datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%b %d %Y %H:%M:%S.%f, ")
    try:
        f=open(f"log.log",'a')
        if withTime:
            f.write(timestamp+msg+"\n")
        else:
            f.write(msg+"\n")
        f.close()
    except:
        pass