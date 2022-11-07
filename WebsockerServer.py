from time import sleep
from urllib import response
import websockets
import asyncio
import json
import sys

class WebsocketServer:
    def __init__(self,port):
        self.port=port
        self.grid_dic={}
        self.conf_dic={}
        self.thread_dict={}

    async def msg_handler(self,websocket,path):
        while True:
            try:
                message= await websocket.recv()
                print(message)
                sleep(5)
                await websocket.send('send'+message)
            except websockets.exceptions.ConnectionClosedError:
                print('客户端已断开连接')
                break
            except websockets.exceptions.InvalidStateErr:
                print('无效状态')
                break
            except Exception as e:
                print('exception')

    def start(self):
        asyncio.get_event_loop().run_until_complete(websockets.serve(self.msg_handler,'0.0.0.0',self.port))
        asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    port=8080
    if len(sys.argv) > 1:
        port=sys.argv[1]
    server=WebsocketServer(port)
    server.start()