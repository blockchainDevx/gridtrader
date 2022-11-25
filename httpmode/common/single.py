import threading
class Singleton():
    _instance_lock=threading.Lock()
    def __new__(cls,*args,**argv):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    orig=super(Singleton,cls)
                    cls._instance = orig.__new__(cls,*args,**argv)  
        return cls._instance