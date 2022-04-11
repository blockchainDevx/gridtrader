import threading
import time

def test(data):
    while True:
        print(data)
        time.sleep(1)
th31=[]

def create():
    th3=threading.Thread(target=test,args={3})
    th3.start()
    th31.append(th3)

th1=threading.Thread(target=test,args={1})
th2=threading.Thread(target=test,args={2})
th4=threading.Thread(target=create)

th4.start()
th1.start()
th2.start()