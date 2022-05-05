#!/usr/bin/python
# -*- coding: UTF-8 -*-
from lib2to3.pgen2.token import STAR
import threading
import sys
from tokenize import group
from xml.dom.minidom import Identified
sys.path.append('..')
from common import urldata_parse,http_response,ADD,CALC,START,STOP,INIT,DEL
from GridTraderHttp import GridTraderHttp 
import json
from sqlhand import SqlHandler
from crypto import *

'''
数据库结构
    api:{
        "id":1,
        "marketplace":"ok",
        "metadata":"经过加密之后的API信息",
        "subaccount":"cc1"
    }

    tab:{
        "id":"newtab123123",
        "title":"afadsf",
        "metadata":"经过加密之后的网格数据",
    }
'''

'''
api_groups:{
    "okex":{
        "-": [
            {
                'ApiId':"",
                'Exchange':marketpalce,
                'API':{
                    "ApiKey":"",
                    "Secret":"",
                    "Password":"",
                },
                'Subaccount':substr,
                'Useable':False
            },
            {
                'ApiId':"",
                'Exchange':marketpalce,
                'API':{
                    "ApiKey":"",
                    "Secret":"",
                    "Password":"",
                },
                'Subaccount':substr,
                'Useable':False
            },
            ...
        ]
        "groupid1":{
            'available':False,
            'apilist':[
            {
                'ApiId':"",
                'Exchange':marketpalce,
                'API':{
                    "ApiKey":"",
                    "Secret":"",
                    "Password":"",
                },
                'Subaccount':substr,
                'Useable':False
            },
            {
                'ApiId':"",
                'Exchange':marketpalce,
                'API':{
                    "ApiKey":"",
                    "Secret":"",
                    "Password":"",
                },
                'Subaccount':substr,
                'Useable':False
            },
            ...
        ]}
    },
    "ftx":{
        "-": [          #-表示没有被纳入集合的api组 
            {
                'ApiId':"",
                'Exchange':marketpalce,
                'API':{
                    "ApiKey":"",
                    "Secret":"",
                    "Password":"",
                },
                'Subaccount':substr,
                'Useable':False
            },
            {
                'ApiId':"",
                'Exchange':marketpalce,
                'API':{
                    "ApiKey":"",
                    "Secret":"",
                    "Password":"",
                },
                'Subaccount':substr,
                'Useable':False
            },
            ...
        ]
        "groupid2":{
            'avilable':False,
            'apilist':[   #groupid2表示组id   
            {
                'ApiId':"",
                'Exchange':marketpalce,
                'API':{
                    "ApiKey":"",
                    "Secret":"",
                    "Password":"",
                },
                'Subaccount':substr,
                'Useable':False
            },
            {
                'ApiId':"",
                'Exchange':marketpalce,
                'API':{
                    "ApiKey":"",
                    "Secret":"",
                    "Password":"",
                },
                'Subaccount':substr,
                'Useable':False
            },
            ...
        ]}
    }
}

grids_map:{
    "key":{
        "title":tab1,
        "content":{
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
            'Factor':0,
            'GroupId':'-'
        }
    }
}

trade_maps:{
    "key1":[{ #key为tab的key
        "trade":gridtradehttp,
        "thread":thread,
        }],
}

apiid_maps:{
    "apiid1":{
        'Exchange':marketpalce,
        'API':{
            "ApiKey":"",
            "Secret":"",
            "Password":"",
        },
        'Subaccount':substr,
        'Useable':False
    },
    "apiid2":{
        'Exchange':marketpalce,
        'API':{
            "ApiKey":"",
            "Secret":"",
            "Password":"",
        },
        'Subaccount':substr,
        'Useable':False
    },
    ...
}

group_maps:{
    "groupid1":{
        "groupname":"",
        "exchange":"",
        "apiid_arr":[
            "1",
            "2",
            ...
        ]
    },
    "groupid2":{
        "groupname":"",
        "exchange":"",
        "apiid_arr":[
            "3",
            "4",
            ...
        ]
    }   
}
'''

class GridManager():
    _instance_lock=threading.Lock()
    def __init__(self):
        self.grids_map={}
        self.api_groups={}
        self.trades_map={}
        self.group_infos={}
    
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
        api_maps=self.get_accounts()
        #读取数据库获取所有保存的tab页数据
        self.get_tabs()
        #读取数据库获取所有的API分组信息
        groups=self.get_group_apis()

        #遍历api_map和api_group,
        self.api_groups_compose(api_maps,groups)



        
    
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
        apis_map={}
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
                apis_map[f'{id}']={
                    'Exchange':marketpalce,
                    'API':data,
                    'Subaccount':substr,
                    'Useable':False
                }
        return apis_map
        
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
                    'content':data,
                    'available':False,
                }

    def get_group_apis(self):
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
        _,_,groups=SqlHandler.Execute(sql)

        r'''
        +-----------+-------------+------+-----+---------+-------+
        | Field     | Type        | Null | Key | Default | Extra |
        +-----------+-------------+------+-----+---------+-------+
        | groupid   | int         | YES  |     | NULL    |       |
        | groupname | varchar(64) | YES  |     | NULL    |       |
        | exchange  | varchar(64) | YES  |     | NULL    |       |
        +-----------+-------------+------+-----+---------+-------+
        ''' 
        sql='select * from `group_infos`'
        _,_,group_infos=SqlHandler.Execute(sql)

        groups={}
        for item in group_infos:
            id=item.get('groupid')
            name=item.get('groupname')
            exchange=item.get('exchange')

            if id==None or exchange==None:
                continue
            
            self.group_infos[f'{id}']=name

            arr=[]
            for item in groups:
                groupid= item.get('groupid')
                apiid= item.get('apiid')
                if groupid==None or apiid==None:
                    continue
                if id==groupid:
                    arr.append(id)
            groups[f'{id}']={
                'groupname':name,
                'exchange':exchange,
                'apiid_arr':arr
            }
        return groups
    
    #api数据与组数据聚合
    def api_groups_compose(self,apis,groups):
        useable_list=[]
        for groupid,value in groups.items():
            exchange=value.get('exchange')

            #初始化时,group没有被使用
            self.api_groups[f'{exchange}'][f'{groupid}']['available']=False

            apiid_arr=value.get('apiid_arr')
            if apiid_arr==None:
                continue
            for index in range(0,len(apiid_arr)):
                api_data=apis.get(apiid_arr[index])
                if api_data==None:
                    continue

                #将API数据按照组分类
                self.api_groups[f'{exchange}'][f'{groupid}']['apilist'].append(
                    {
                        'ApiId':apiid_arr[index],
                        'Exchange':api_data['Exchange'],
                        'API':api_data['API'],
                        'Subaccount':api_data['Subaccount'],
                        'Useable':False
                    })
                useable_list.append(apiid_arr[index])
        
        #api集合与使用的use_list相减得到未被分配到组的apiid列表
        diff=list(set(apis.keys())-set(useable_list))
        for index in range(0,len(diff)):
            api_data=apis.get(diff[index])
            if api_data==None:
                continue
            exchange=api_data['Exchange']
            if exchange==None:
                continue
            self.api_groups[f'{exchange}']['-'].append({
                'ApiId':diff[index],
                'Exchange':api_data['Exchange'],
                'API':api_data['API'],
                'Subaccount':api_data['Subaccount'],
                'Useable':False
                })

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
                    'GroupId':'-' 
                }
            }
    
    def get_API_by_exchange(self,exchange):
        exchange_map=self.api_groups[f'{exchange}']
        if exchange_map==None:
            return False,f"根据交易所名称{exchange}没找到API组",None
        api_list=exchange_map.get('-')
        if api_list==None:
            return False,f"没有{exchange}的API"
        if len(api_list)>0:
            api=api_list[0]
            return True,"",api
        return False,f'没有{exchange}的API'

    def get_useable_API_by_ex(self,exchange):
        exchange_map=self.api_groups[f'{exchange}']
        if exchange_map==None:
            return False,"根据交易所名称{exchange}未找到API",None
        api_list=exchange_map.get('-')
        if api_list==None:
            return False,"根据交易所名称{exchange}未找到API",None
        for index in range(0,len(api_list)):
            if api_list[index]['Useable']==False:
                return True,"OK",api_list[index]
        return False,"",f'根据交易所名称{exchange}没有找到合适的API',None

    def change_available_by_Ex_And_APIId(self,exchange,apiid,flag):
        exchange_map=self.api_groups['f{exchange}']
        if exchange_map!=None:
            api_list=exchange_map.get(f'-')
            if api_list!=None and len(api_list)>0:
                for index in range(0,len(api_list)):
                    if api_list[index]['ApiId']==apiid:
                        api_list[index]['ApiId']=flag

    
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
                    'Ratio':data['Ratio'],
                    'GroupId':data['GroupId']
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
            item['content']['GroupId']=data['GroupId']

    def grid_init(self):
        data=[]
        for key,value in self.grids_map.items():
            data.append({
                'key':key,
                'title':value['title'],
                'content':value['content']
            })
        return http_response(INIT,'',0,'OK',data)
    
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
        
        #检查组是否已启用
        if id in self.trades_map:
            return http_response(START,id,-1,'网格开启错误,网格已经开启')
        
        #根据传入的key查找网格配置数据
        conf_data=self.grids_map.get(id)
        if conf_data==None: #没找到数据,返回错误
            return http_response(START,id,-1,'网格开启错误,未根据页面编号找到网格数据')
        
        #检查组是否已启用
        # if conf_data['available']==True:
        #     return http_response(START,id,-1,'网格开启错误,网格已经开启')

        if abs(conf_data['content']['Ratio']) <=sys.float_info.epsilon: #没有配置比例,只开启一个
            flag,errmsg=self.create_trade(id,conf_data)
            if flag==False:
                return http_response(START,id,-1,errmsg)
        else: #有配置比例,按照给的组ID启动一批网格
            flag,errmsg=self.create_trades(conf_data)
            if flag==False:
                return http_response(START,id,-1,errmsg)
        #网格开启成功,将网格配置状态设置为已用
        self.set_grid_state(id,True)
        return http_response(START,id,0,'OK')
    
    def set_grid_state(self,key,state):
        if key in self.grids_map:
            self.grids_map[f'{key}']['available']=state
    
    def create_trade(self,id,data,ratio=1):
        flag,errmsg,api=self.get_useable_API_by_ex(data['content']['Exchange'])
        if flag==False:
            return False,'没有找到能使用的API密钥'
        trader=GridTraderHttp()
        flag,errmsg=trader.read_config_by_obj(api['API'],data,ratio)
        if flag==False:
            return flag,errmsg
        flag2,errmsg2=trader.start(ratio)
        if flag2==False:
            return flag2,errmsg2
        thread= threading.Thread(target=trader.order_monitor)
        thread.start()
        self.trades_map[id].append({
            'trader':trader,
            'thread':thread
        })

        self.change_available_by_Ex_And_APIId(data['content']['Exchange'],api['ApiId'],True)
        return True,"OK"

    def create_trades(self,data):
        #根据配置中的交易所名称获取交易所的所有API数据
        exchange=data['content']['Exchange']
        if exchange==None:
            return False,'网格数据错误,没有填写交易所'
        exchange_maps=self.api_groups.get(f'{exchange}')
        if exchange_maps==None:
            return False,f'没有与{exchange}相关的API数据'

        #根据配置中的组ID获取该组的所有API数据
        groupid=data['content']['GroupId']
        if groupid==None:
            return False,'网格数据错误,没有填写组数据'

        #获取组名称
        groupname=''
        groupname1=self.group_infos[f'{groupid}']
        if groupname1!=None:
            groupname=groupname1

        #获取组数据
        group=exchange_maps.get(f'{groupid}')
        if group==None or len(group['apilist']):
            return False,f'网格数据错误,没有找到组{groupname}相关的API数据'
        
        #检查组是否已占用
        if group['available']==True:
            return False,f'组{groupname}已被占用'
        
        #批量启动数据
        apilist=group['apilist']

        factor=float(data['content']['Factor'])
        for i in range(0,len(apilist)):
            factor_mt=(factor+1)**i
            trader=GridTraderHttp()
            flag,errmsg=trader.read_config_by_obj(apilist[i]['API'],data,factor_mt)
            if flag==False:
                return flag,errmsg
            flag2,errmsg2=trader.start(factor_mt)
            if flag2==False:
                return flag2,errmsg2
            thread= threading.Thread(target=trader.order_monitor)
            thread.start()
            self.trades_map[id].append({
                'trader':trader,
                'thread':thread
            })
        return True,'OK'
        pass
    
    def  grid_stop(self,data):
        id=data.get('id')
        if id==None:
            return http_response(STOP,'',-1,'参数错误')
        trade=self.trades_map.get(f'{id}')
        if trade==None:
            return http_response(STOP,id,-1,'该网格未开启')
        trade['trader'].stop()
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
            elif strs[0]==INIT:
                return self.grid_init()
            

    def post_handler(self,path,body):
        if path==ADD:
            return self.grid_add(body)
        elif path==START:
            return self.grid_start(body)
        elif path==STOP:
            return self.grid_stop(body)
        
        