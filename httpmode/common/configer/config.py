import json
import sys
sys.path.append('..')

from ..single import Singleton

class Config(Singleton):
    def Init(self,file):
        try:
            f = open(file,mode='r')
            data = json.load(f)
            self.mysql=data['mysql']
            self.glob=data['global']
            f.close()
        except Exception as e:
            print(str(e))
            pass
    