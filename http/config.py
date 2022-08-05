import json
import threading
import os
from common import Singleton

class Config(Singleton):
    def Init(self,file):
        try:
            print(os.getcwd())
            f = open('.\http\\'+file,mode='r')
            data = json.load(f)
            self.mysql=data['mysql']
            self.glob=data['global']
            f.close()
        except Exception as e:
            print(str(e))
            pass
    