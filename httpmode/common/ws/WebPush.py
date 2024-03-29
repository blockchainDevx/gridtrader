from sqlite3 import Date
import sys
sys.path.append('..')
from common.single import Singleton
import threading
import asyncio
import websockets
import datetime
import json

WS_OPEN='wsconnect'
WS_PING='wsping'
WS_PONG='wspong'

def http_response(msgtype,id,errid,errmsg,data={}):
    return json.dumps({
        'msgtype':msgtype,
        'id': id,
        'errid':errid,
        'errmsg':errmsg,
        'data':data
    })

class WebPush(Singleton):
    __thread={}
    __sockets=[]
    __port=8082
    __cb={}
    __lock=threading.Lock()
    __id=0
    __loop={}

    def init(self,port):
        self.__port=port

    async def add_socket(self,websocket):
        self.__lock.acquire()
        self.__sockets.append(websocket)
        self.__lock.release()
        self.__id=self.__id+1
        await websocket.send(http_response(WS_OPEN,self.__id,0,'OK',str(datetime.datetime.now())))

    def sendmsg(self,data,datatype):
            # print('sendmsg'+data)
            self.__lock.acquire()
            for websocket in self.__sockets:
                try:
                    self.__id=self.__id+1
                    ret=asyncio.run_coroutine_threadsafe(websocket.send(http_response(datatype,self.__id,0,"OK",data)),self.__loop)
                    ret.result()
                except Exception as e:
                    print('ws发送错误'+str(e))
                    if websocket in self.__sockets:
                        self.__sockets.remove(websocket)
                    
            self.__lock.release()


    async def msg_handler(self,websocket,path):

        while True:
            message=await websocket.recv()
            # print(message)
            try:
                data=json.loads(message)
                msgtype=data.get('msgtype')
                if msgtype != None and msgtype == WS_PING:
                    # print("msgtype"+msgtype)
                    self.__id=self.__id+1
                    await websocket.send(http_response(WS_PONG,self.__id,0,"OK",str(datetime.datetime.now())))
                    # self.sendmsg(http_response(PONG,self.__id,0,"OK",str(datetime.datetime.now())))
            except Exception as e:
                await websocket.send(http_response(WS_PONG,self.__id,-1,"数据解析错误",str(datetime.datetime.now())))
                print(str(e))
                pass


    async def run(self,websocket,path):
        while True:
            try:
                await self.add_socket(websocket)
                await self.msg_handler(websocket,path)
            except websockets.exceptions.ConnectionClosedError:
                print('客户端已断开连接')

                self.__lock.acquire()
                if websocket in self.__sockets:
                    self.__sockets.remove(websocket)
                self.__lock.release()

                break
            except websockets.exceptions.InvalidStateErr:

                print('无效状态')
                break
            except Exception as e:
                print('exception '+str(e))


    def listener(self):
        self.__loop=asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)
        self.__loop.run_until_complete(websockets.serve(self.run,'0.0.0.0',self.__port))
        self.__loop.run_forever()

    def start(self):
        self.__thread= threading.Thread(target=self.listener)
        self.__thread.start()


