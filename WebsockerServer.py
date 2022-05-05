import websockets
from GridTraderNet import *
import asyncio
import json
import sys
import threading

'''
    request msg:{
        "msgtype":"new"
        'id':,
        "data":{
            "Exchange":"ftx",
            "ApiKey":"",
            "Secret":"",
            "Password":"",
            "Symbol":"",
            "PriceReserve":,
            "QtyReserve":,
            "UpBound":,
            "LowBound":,
            "GridQty":,
            "Ammount":,
            "Stop":
        }
    }
    response msg:{
        "msgtype":"new",
        'id':,
        "errno":0,
        "errmsg":"ok",
        "data":{
            "Id':,
            "RatioPerGrid":,
            "FundPerGrid":,
            "ProfitPerGrid":,
            "NetProfit":,
            "LastPrice":,
            "GridPriceList":[{
                "UpPrice":,
                "LowPrice":,
            },{
                "UpPrice":,
                "LowPrice":
            }],
            "EntryQty":,
            "NetEntryQty":,
            "AmountSpent":,
            "RemainingAmount":
        }
    }
'''

class WebsocketServer:
    _instance_lock=threading.Lock()
    def __init__(self,port):
        self.port=port
        self.grid_dic={}
        self.conf_dic={}
        self.thread_dict={}

    def __new__(cls,*args,**argv):
        if not hasattr(WebsocketServer, "_instance"):
            with WebsocketServer._instance_lock:
                if not hasattr(WebsocketServer, "_instance"):
                    WebsocketServer._instance = object.__new__(cls)  
        return WebsocketServer._instance

    async def msg_handler(self,websocket,path):
        async for message in websocket:
            js_data=WebsocketServer.json_parse(message)
            if js_data!=None:
                if js_data['msgtype'] =='connect':
                    print('connect')
                    await websocket.send(WebsocketServer.obj_to_json('connect',0,'ok',{}))
                elif js_data['msgtype'] == 'calc':
                    ret_str=self.calc_handler(js_data)
                    print('return: '+ret_str)
                    await websocket.send(ret_str)
                elif js_data['msgtype']=='start':
                    self.start_grid(js_data['id'])
                    retstr= WebsocketServer.obj_to_json('start',0,'ok',{})
                    await websocket.send(retstr)
                elif js_data['msgtype']=='stop':
                    self.stop_grid(js_data['id'])
                    retstr= WebsocketServer.obj_to_json('start',0,'ok',{})
                    await websocket.send(retstr)
                elif js_data['msgtype']=='delete':
                    self.delete_grid(js_data['id'])
                    retstr= WebsocketServer.obj_to_json('start',0,'ok',{})
                    await websocket.send(retstr)
                    
    #收到新的网格请求数据:
    def calc_handler(self, js_data):
        print('data,'+str(js_data))
        data=js_data['data']
        flag,msg=GridTraderNet.parms_check(data)
        print('return: '+str(flag)+msg)
        if flag==False:
            #参数配置错误
            return WebsocketServer.obj_to_json('calc',-1,msg,{})
        else:
            #将新网格加入列表中 
            flag,errmsg,data1=GridTraderNet.grid_calc(data)
            print('exchange connect:'+str(flag)+errmsg+str(data1))
            errid=-1
            if flag==True:
                errid=0
                errmsg='ok'
                uid=js_data['id']
                self.conf_dic[f'{uid}']=data1
            return WebsocketServer.obj_to_json('calc',errid,errmsg,data1)

    #开启网格
    def start_grid(self,id):
            grid=self.conf_dic.get(f'{id}')
            if grid !=None:
                #根据id找到网格
                trader=GridTraderNet()
                flag,errmsg=trader.read_config_by_obj(grid[f'{id}'])
                if flag ==False:
                    return WebsocketServer.obj_to_json('start',-1,errmsg)
                thread=threading.Thread(target=trader.grid_start())
                trader.grid_start()
                self.thread_dict[f'{id}']=thread
                self.grid_dic[f'{id}']=trader

    def stop_grid(self,id):
            grid=self.grid_dic.get[f'{id}']
            if grid!=None:
                grid.grid_stop()
            thread= self.thread_dict.get[f'{id}']
            if thread!=None:
                del self.grid_dic[f'{id}']
    
    def delete_grid(self,id):
        grid=self.grid_dic.get[f'{id}']
        if grid!=None:
            grid.grid_stop()
            

    @staticmethod
    def obj_to_json(msgtype,errid,errmsg,data={}):
        obj={
            'msgtype':msgtype,
            'errid':errid,
            'errmsg':errmsg,
            'data':data}
        return json.dumps(obj)

    def create_new_grid_obj(self,jsondata):
        grid_obj=GridTraderNet()

    # @staticmethod
    # def GridConfData(data):
    #     return {
    #         "Exchange":str(data['Exchange']),
    #         "ApiKey":str(data['ApiKey']),
    #         "Secret":str(data['Secret']),
    #         "Password":str(data['Password']),
    #         "Symbol":str(data['Symbol']),
    #         "PriceReserve":float(data['PriceReserve']),
    #         "QtyReserve":float(data['QtyReserve']),
    #         "UpBound":float(data['UpBound']),
    #         "LowBound":,
    #         "GridQty":,
    #         "Ammount":,
    #         "Stop":
    #     }

    @staticmethod
    def json_parse(str):
        try:
            js_data=json.loads(str)
            return js_data
        except:
            return None

    def start(self):
        asyncio.get_event_loop().run_until_complete(websockets.serve(self.msg_handler,'0.0.0.0',self.port))
        asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    port=8080
    if len(sys.argv) > 1:
        port=sys.argv[1]
    server=WebsocketServer(port)
    server.start()