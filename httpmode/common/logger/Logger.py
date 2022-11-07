from ..common import Singleton
from datetime import datetime
import pytz

class Logger(Singleton):
    def log(self,msg,withTime=True):
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