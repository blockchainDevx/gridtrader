#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import sys
from xml.dom.minidom import Identified
sys.path.append('..')
from common import urldata_parse,http_response,ADD,CALC,START,STOP
from GridTraderHttp import GridTraderHttp 
import json
from sqlhand import SqlHandler
from crypto import *

'''
    api:{
        "id":1,
        "marketplace":"ok",
        "metadata":"经过加密之后的API信息",
        "subaccount":"cc1"
    }
'''
'''
    tab:{
        "id":"newtab123123",
        "title":"afadsf",
        "metadata":"经过加密之后的网格数据",
    }
'''

class GridManager():
    _instance_lock=threading.Lock()
    def __init__(self):
        self.grids_map={}
        self.apis_map={}
        self.trades_map={}
    
    def __new__(cls,*args,**argv):
        if not hasattr(GridManager, "_instance"):
            with GridManager._instance_lock:
                if not hasattr(GridManager, "_instance"):
                    GridManager._instance = object.__new__(cls)  
        return GridManager._instance
    
    @staticmethod
    def metadata_encode(metadata):
        try:
            str=json.dump(metadata)
            return True, Encode(str)
        except:
            return False,None
        
    @staticmethod
    def metadata_decode(str):
        try:
            str_data=Decode(str)    
            data=json.loads(str_data)
            return True,data
        except:
            return False,None
    
    def init(self):
        #读取数据库获取所有的API
        self.get_accounts()
        #读取数据库获取所有保存的tab页数据
        self.get_tabs()
        #读取数据库获取所有的API分组信息
        groups=self.get_groups()
        group_infos=self.get_group_infos()
        for item in groups:
    
    def get_accounts(self):
        r'''
        +-------------+---------------+------+-----+---------+-------+
        | Field       | Type          | Null | Key | Default | Extra |
        +-------------+---------------+------+-----+---------+-------+
        | id          | int           | YES  |     | NULL    |       |
        | metadata    | varchar(4096) | YES  |     | NULL    |       |
        | marketpalce | varchar(64)   | YES  |     | NULL    |       |
        | subaccount  | varchar(64)   | YES  |     | NULL    |       |
        +-------------+---------------+------+-----+---------+-------+
        '''
        sql='select * from `api_datas`'
        flag,count,res=SqlHandler.Execute(sql)
        if flag==True:
            for i in range(0,len(res)):
                metadata=res[i].get('metadata')
                id=res[i].get('id')
                marketpalce=res[i].get('marketplace')
                subaccount=res[i].get('subaccount')
                if metadata==None or id ==None or marketpalce==None:
                    continue
                _,data=GridManager.metadata_decode(metadata)
                if data==None:
                    continue
                substr=''
                if subaccount!=None:
                    substr=subaccount
                self.apis_map[f'{id}']={
                    'Exchange':marketpalce,
                    'API':data,
                    'Subaccount':substr
                }
    
        
    def get_tabs(self):
        r'''
        +----------+---------------+------+-----+---------+-------+
        | Field    | Type          | Null | Key | Default | Extra |
        +----------+---------------+------+-----+---------+-------+
        | id       | varchar(128)  | YES  |     | NULL    |       |
        | metadata | varchar(4096) | YES  |     | NULL    |       |
        | title    | varchar(128)  | YES  |     | NULL    |       |
        +----------+---------------+------+-----+---------+-------+
        '''
        sql='select * from `tabs`'
        flag,count,res=SqlHandler.Execute(sql)
        if flag==True:
            for i in range(0,count):
                metadata=res[i].get('metadata')
                id=res[i].get('id')
                title=res[i].get('title')
                if metadata==None or id==None or title==None:
                    continue
                _,data=GridManager.metadata_decode(metadata)
                if data==None:
                    continue
                self.grids_map[f'{id}']={
                    'title':title,
                    'content':data
                }
        
    def get_groups(self):
        r'''
        +---------+--------------+------+-----+---------+-------+
        | Field   | Type         | Null | Key | Default | Extra |
        +---------+--------------+------+-----+---------+-------+
        | groupid | int          | YES  |     | NULL    |       |
        | apiid   | int          | YES  |     | NULL    |       |
        | id      | int unsigned | NO   | PRI | NULL    |       |
        +---------+--------------+------+-----+---------+-------+
        '''
        sql= 'select * from `groups`'
        _,_,res=SqlHandler.Execute(sql)
        return res
    
    def get_group_infos(self):
        r'''
        +----------+-------------+------+-----+---------+-------+
        | Field    | Type        | Null | Key | Default | Extra |
        +----------+-------------+------+-----+---------+-------+
        | groupid  | int         | YES  |     | NULL    |       |
        | grouname | varchar(64) | YES  |     | NULL    |       |
        +----------+-------------+------+-----+---------+-------+
        '''
        sql='select * from `group_infos`'
        _,_,res=SqlHandler.Execute(sql)
        return res
    
    def grid_add(self,data):
        title=data.get('title')
        key=data.get('key')
        if title==None or key == None:
            return http_response(ADD,'',-1,'添加网格配置表失败')
        else:
            self.add_grid_data(key,title)
            return http_response(ADD,f'{key}',0,'ok')
        
    def add_grid_data(self,id,title):
        self.grid_map[f'{id}']={
                'title':title,
                'content':{
                    'Exchange': '',
                    'Symbol': '', 
                    'PriceReserve': 6,
                    'QtyReserve': 6, 
                    'Open': 0, 
                    'UpBound': 0, 
                    'LowBound': 0, 
                    'GridQty': 0, 
                    'Stop': 0, 
                    'Amount': 0, 
                    'Ratio':0, 
                }
            }
    
    def get_API_by_exchange(self,exchange):
        for _,value in self.apis_map.items():
            if value['Exchange']==exchange:
                return {
                    "ApiKey":value['API']['ApiKey'],
                    "Secret":value['API']['Secret'],
                    'Password':value['API']['Password'],
                    'Subaccount':value['Subaccount']
                }
        return None   
    
    def update_tab_by_id(self,id,title,data):
        item=self.grids_map.get(id)
        if item==None:
            self.grids_map[f'{id}']={
                'title':title,
                'content':{
                    'Exchange':data['Exchange'],
                    'Symbol':data['Symbol'],
                    'PriceReserve':data['PriceReserve'],
                    'QtyReserve':data['QtyReserve'],
                    'Open':data['Open'],
                    'UpBound':data['UpBound'],
                    'LowBound':data['LowBound'],
                    'GridQty':data['GridQty'],
                    'Stop':data['Stop'],
                    'Amount':data['Amount'],
                    'Ratio':data['Ratio']
                }
            }
        else:
            item['title']=title
            item['content']['Exchange']=data['Exchange']
            item['content']['Symbol']=data['Symbol']
            item['content']['PriceReserve']=data['PriceReserve']
            item['content']['QtyReserve']=data['QtyReserve']
            item['content']['Open']=data['Open']
            item['content']['UpBound']=data['UpBound']
            item['content']['LowBound']=data['LowBound']
            item['content']['GridQty']=data['GridQty']
            item['content']['Stop']=data['Stop']
            item['content']['Amount']=data['Amount']
            item['content']['Ratio']=data['Ratio']
    
    def grid_calc(self,data):
        content= data.get('content')
        title=data.get('title')
        id=data.get('key')
        if content==None or id==None or title==None:
            return  http_response(CALC,'', -1,'计算数据格式错误')
        try:
            json_data=json.loads(content)
            flag,msg=GridTraderHttp.parms_check(json_data)
            if flag==False:
                return http_response(CALC,id,-1,msg)
            else:
                #参数检测完之后更新缓存中的数据
                self.update_tab_by_id(id,title,content)
                
                #根据配置中的exchange获取第一份api数据
                api=self.get_API_by_exchange(json_data['Exchange'])
                if api==None:
                    exc=json_data['Exchange']
                    return http_response(CALC,id,-1,f'根据市场{exc}没有找到api')
                
                #计算数据
                flag,errmsg,data1=GridTraderHttp.grid_calc(api,json_data)
                if flag==False:
                    return http_response(CALC,id,-1,errmsg)
                else:
                    return http_response(CALC,id,0,errmsg,data1)
        except:
            return  http_response(CALC,id,-1,'计算数据格式错误')

    def grid_start(self,data):
        id=data.get('id')
        if id==None:
            return http_response(START,'',-1,'网格开启错误,参数错误')
        else:
            #根据传入的key查找网格配置数据
            data=self.grids_map.get(id)
            if data==None: #没找到数据,返回错误
                return http_response(START,id,-1,'网格开启错误,未根据页面编号找到网格数据')
            else: #找到网格数据,启动网格
                pass
    
    def create_trade(self,data):
        
        pass
    
    def  grid_stop(self,data):
        pass
        

    def get_handler(self,path):
        if len(path)==0:
            return {
                'errmsg':'请求数据格式错误'
            }
            '''
            /api/calc?
            title=123&
            key=newTab1651074742690&
            content={"priceDecimal":6,"lotDecimal":6,"initialPrice":0,"maxPrice":0,"minPrice":0,"quantity":0,"stopPrice":0,"amount":0,"ratio":0}
            '''
        strs=path.split('?')
        count = len(strs)
        if count==0 or count!=2 :
            return {
                'errmsg':'请求数据格式错误'
            }
        else:
            data=urldata_parse(strs[1])
            if strs[0]==CALC:
                return self.grid_calc(data)
            

    def post_handler(self,path,body):
        if path==ADD:
            return self.grid_add(body)
        elif path==START:
            return self.grid_start(body)
        elif path==STOP:
            return self.grid_stop(body)
        
        