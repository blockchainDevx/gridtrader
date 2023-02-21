from common.common import LIMIT,SELL,RecordData
from common.single import Singleton
from common.thread_utils import thread_pool
import time

import threading
            
class SPQuoteMgr(Singleton):
    def __init__(self):
        self._lock=threading.RLock()
        self._task_maps={}
        self._thread={}
        
        thread_pool.init_thread_pool_executor(5,'EventTasks')
        pass
    
    def addtask(self,taskobj):
        with self._lock:
            self._task_maps[f'{str(taskobj)}']=taskobj
    
    def deltask(self,taskname):
        with self._lock:
            self._deltask(taskname)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    def _deltask(self,taskname):
        if taskname in self._task_maps:
            del self._task_maps[taskname]
    
    def starttask(self):
        lis=set()
        while True:
            with self._lock:
                for taskcb,taskname in self._task_maps:
                    lis.add((thread_pool.threadPoolExecutor.submit(taskcb.run),taskname))
                for item in lis:
                    if item[0].result() == True:
                        self.deltask(item[1])
                lis.clear()
            time.sleep(1)        
                
    def async_starttask(self):
        self._thread=threading.Thread(target=self.starttask)
        self._thread.start()
        