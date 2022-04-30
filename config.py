import json
import threading

class Config():
    _instance_lock=threading.Lock()
    def __new__(cls,*args,**argv):
        if not hasattr(Config, "_instance"):
            with Config._instance_lock:
                if not hasattr(Config, "_instance"):
                    Config._instance = object.__new__(cls)  
        return Config._instance
    
    def __init__(self) -> None:
        self.mysql={}
        self.glob={}
        
    def Init(self,path):
        try:
            f = open(path)
            data = json.load(f)
            self.mysql=data['mysql']
            self.glob=data['global']
            f.close()
        except:
            pass

        
    