import threading
import time


def test(data,lock):
    if lock!=None:
        with lock:
            print(str(time.time())+'   '+str(data))
            time.sleep(1)
    else:
        print(str(time.time())+'   '+str(data))
        time.sleep(1)
    # while True:
    #     print(data)
    #     time.sleep(1)
th31=[]

def create():
    gthlck=threading.Lock()
    #gthlck=None
    # gthlck=None
    for i in range(0,1000):
        th3=threading.Thread(target=test,args=(i,gthlck,))
        th3.start()
        th31.append(th3)

th6={}
class test2:
    def test(self,data):
        th6=threading.Thread(target=test,args=('test22323',))
        th6.start()

th1=threading.Thread(target=test,args={1})
th2=threading.Thread(target=test,args={2})
th4=threading.Thread(target=create)

test23=test2()
th5=threading.Thread(target=test23.test,args=('tes2',))

# th4.start()
# th1.start()
# th2.start()
# th5.start()
create()
input('')