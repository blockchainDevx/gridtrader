from common.single import Singleton
from common.thread_utils import thread_pool
from common.common import Record,LOG_STORE
from concurrent.futures import as_completed

import time

import threading

SLEEP_MILSEC=1000
            
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
        Record('订单 止盈/止损 任务线程监控开启',level=LOG_STORE)
        lis=[]
        while True:
            start=time.time()
            with self._lock:
                for taskcb in self._task_maps.values():
                    
                    lis.append(thread_pool.threadPoolExecutor.submit(taskcb.run))
            for item in as_completed(lis):
                if item.result()[0] == True:
                    self.deltask(item.result()[1])
            lis.clear()
            end=time.time()
            interval=int(round(end-start)*1000)
            if interval < SLEEP_MILSEC:
                time.sleep((SLEEP_MILSEC-interval)/1000)
            # print(f'{time.time()}')
                   
                
    def async_starttask(self):
        self._thread=threading.Thread(target=self.starttask)
        self._thread.start()
        