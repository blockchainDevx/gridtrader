#!/usr/bin/python
# -*- coding: UTF-8 -*-
from lib2to3.pgen2.token import STAR
import threading
import sys
from tokenize import group
from xml.dom.minidom import Identified
sys.path.append('..')
from common import Singleton,urldata_parse,http_response,ADD,CALC,START,STOP,INIT,DEL,UPDATE,QUERY
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
                'available':False
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
                'available':False
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
                'available':False
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
                'available':False
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
                'available':False
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
                'available':False
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
                'available':False
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
                'available':False
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
        'available':False
    },
    "apiid2":{
        'Exchange':marketpalce,
        'API':{
            "ApiKey":"",
            "Secret":"",
            "Password":"",
        },
        'Subaccount':substr,
        'available':False
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

class GridManager(Singleton):
    _instance_lock=threading.Lock()
    grids_map={}
    api_groups={}
    trades_map={}
    group_infos={}
    # def __init__(self):
    #     self.grids_map={}
    #     self.api_groups={}
    #     self.trades_map={}
    #     self.group_infos={}
    
    @staticmethod
    def metadata_encode(metadata):
        try:
            str=json.dumps(metadata)
            return True, Encode(str)
        except Exception as e:
            print(str(e))
            return False,None 

    @staticmethod
    def metadata_encode2(jsstr):
        return True,Encode(jsstr)
        
    @staticmethod
    def metadata_decode(str):
        try:
            str_data=Decode(str)    
            data=json.loads(str_data)
            return True,data
        except Exception as e:
            print(str(e))
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
        flag,count,res=SqlHandler.Query(sql)
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
                    'available':False
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
        flag,count,res=SqlHandler.Query(sql)
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
                print(str(data))
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
        _,_,group_datas=SqlHandler.Query(sql)

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
        _,_,group_infos=SqlHandler.Query(sql)

        groups={}
        for item in group_infos:
            id=item.get('groupid')
            name=item.get('groupname')
            exchange=item.get('exchange')

            if id==None or exchange==None:
                continue
            
            self.group_infos[f'{id}']=name

            arr=[]
            for item in group_datas:
                groupid= item.get('groupid')
                apiid= item.get('apiid')
                if groupid==None or apiid==None:
                    continue
                if id==groupid:
                    arr.append(apiid)
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
            
            exchanges=self.api_groups.get(f'{exchange}')
            if exchanges == None:
                self.api_groups[f'{exchange}']={}

            self.api_groups[f'{exchange}'][f'{groupid}']={}
            #初始化时,group没有被使用
            self.api_groups[f'{exchange}'][f'{groupid}']['available']=False

            apiid_arr=value.get('apiid_arr')
            if apiid_arr==None:
                continue
            for index in range(0,len(apiid_arr)):
                api_data=apis.get(f'{apiid_arr[index]}')
                if api_data==None:
                    continue

                #将API数据按照组分类
                if 'apilist' not in self.api_groups[f'{exchange}'][f'{groupid}']:
                    self.api_groups[f'{exchange}'][f'{groupid}']['apilist']=[]
                
                self.api_groups[f'{exchange}'][f'{groupid}']['apilist'].append(
                    {
                        'ApiId':apiid_arr[index],
                        'Exchange':api_data['Exchange'],
                        'API':api_data['API'],
                        'Subaccount':api_data['Subaccount'],
                    })
                useable_list.append(f'{apiid_arr[index]}')
        
        #api集合与使用的use_list相减得到未被分配到组的apiid列表
        all_ids=apis.keys()
        diff=list(set(all_ids).difference(set(useable_list)))
        for index in range(0,len(diff)):
            api_data=apis.get(diff[index])
            if api_data==None:
                continue
            exchange=api_data['Exchange']
            if exchange==None:
                continue
            meta1= self.api_groups.get(f'{exchange}')
            if meta1==None:
                self.api_groups[f'{exchange}']={}
            meta2=self.api_groups[f'{exchange}'].get('-')
            if meta2==None:
                self.api_groups[f'{exchange}']['-']=[]
            self.api_groups[f'{exchange}']['-'].append({
                'ApiId':diff[index],
                'Exchange':api_data['Exchange'],
                'API':api_data['API'],
                'Subaccount':api_data['Subaccount'],
                'available':False
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
        content={
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
        self.grids_map[f'{id}']={
                'title':title,
                'content':content
            }
        _,metadata=GridManager.metadata_encode(content)
        sql=f'insert into `tabs` (id,metadata,title) values(%(id)s,%(metadata)s,%(title)s)'
        data={'id':id,'metadata':metadata,'title':title}
        SqlHandler.Insert(sql,data)
        
    
    def get_API_by_exchange(self,exchange):
        exchange_map=self.api_groups.get(f'{exchange}')
        if exchange_map==None:
            return False,f"根据交易所名称{exchange}没找到API组",None
        api_list=exchange_map.get('-')
        if api_list==None:
            return False,f"没有{exchange}的API",None
        if len(api_list)>0:
            api=api_list[0]
            return True,"OK",api
        return False,f'没有{exchange}的API',None

    def get_useable_API_by_ex(self,exchange):
        exchange_map=self.api_groups[f'{exchange}']
        if exchange_map==None:
            return False,"根据交易所名称{exchange}未找到API",None
        api_list=exchange_map.get('-')
        if api_list==None:
            return False,"根据交易所名称{exchange}未找到API",None
        for index in range(0,len(api_list)):
            if api_list[index]['available']==False:
                return True,"OK",api_list[index]
        return False,"",f'根据交易所名称{exchange}没有找到合适的API',None

    def change_available_by_Ex_And_APIId(self,exchange,apiid,flag):
        if exchange in self.api_groups:
            if '-' in self.api_groups[f'{exchange}']:
                for index in range(0,len(self.api_groups[f'{exchange}']['-'])):
                    if self.api_groups[f'{exchange}']['-'][index]['ApiId']==apiid:
                        self.api_groups[f'{exchange}']['-'][index]['available']=flag
    
    def change_available_by_Ex_and_groupid(self,exchange,groupid,flag):
        if exchange in self.api_groups:
            if groupid in self.api_groups[f'{exchange}']:
                self.api_groups[f'{exchange}'][f'{groupid}']['available']=flag

    
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
                    'GroupId':data['GroupId'],
                    'Slip':data['Slip']
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
            item['content']['Slip']=data['Slip']

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
                self.update_tab_by_id(id,title,json_data)
                
                #根据配置中的exchange获取第一份api数据
                flag,errmsg,api=self.get_API_by_exchange(json_data['Exchange'])
                if flag==False:
                    return http_response(CALC,id,-1,errmsg)
                
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

        if abs(float(conf_data['content']['Ratio'])) <=sys.float_info.epsilon: #没有配置比例,只开启一个
            flag,errmsg=self.create_trade(id,conf_data['content'])
            if flag==False:
                return http_response(START,id,-1,errmsg)
        else: #有配置比例,按照给的组ID启动一批网格
            flag,errmsg=self.create_trades(id,conf_data['content'])
            if flag==False:
                return http_response(START,id,-1,errmsg)
        #网格开启成功,将网格配置状态设置为已用
        self.set_grid_state(id,True)
        return http_response(START,id,0,'OK')
    
    def set_grid_state(self,key,state):
        if key in self.grids_map:
            self.grids_map[f'{key}']['available']=state
    
    def create_trade(self,id,data,ratio=0):
        flag,errmsg,api=self.get_useable_API_by_ex(data['Exchange'])
        if flag==False:
            return False,'没有找到能使用的API密钥'
        
        #创建网格
        trader=GridTraderHttp()
        flag,errmsg=trader.read_config_by_obj(api,data,ratio)
        if flag==False:
            return flag,errmsg
        
        #启动网格
        flag2,errmsg2,orderid=trader.start(ratio)
        if flag2==False:
            return flag2,errmsg2
        thread= threading.Thread(target=trader.order_monitor,args=(orderid,))
        thread.start()

        #将网格对象数据保存
        self.trades_map[id]={
            'trader':trader,
            'thread':thread,
            'exchange':data['Exchange'],
            'apiid':api['ApiId']
            }

        #将API状态设置为已启用
        self.change_available_by_Ex_And_APIId(data['Exchange'],api['ApiId'],True)
        return True,"OK"

    def create_trades(self,id,data):
        #根据配置中的交易所名称获取交易所的所有API数据
        exchange=data.get('Exchange')
        if exchange==None:
            return False,'网格数据错误,没有填写交易所'

        exchange_maps=self.api_groups.get(f'{exchange}')
        if exchange_maps==None:
            return False,f'没有与{exchange}相关的API数据'

        #根据配置中的组ID获取该组的所有API数据
        groupid=data['GroupId']
        if groupid==None:
            return False,'网格数据错误,没有填写组数据'

        #获取组名称
        groupname=''
        groupname1=self.group_infos[f'{groupid}']
        if groupname1!=None:
            groupname=groupname1

        #获取组数据
        group=exchange_maps.get(f'{groupid}')
        if group==None or len(group['apilist'])==0:
            return False,f'网格数据错误,没有找到组{groupname}相关的API数据'
        
        #检查组是否已占用
        if group['available']==True:
            return False,f'组{groupname}已被占用'
        
        
        

        #批量启动数据
        apilist=group['apilist']
        factor=float(data['Ratio'])
        for i in range(0,len(apilist)):
            factor_mt=factor*i

            #创建网格对象
            trader=GridTraderHttp()
            flag,errmsg=trader.read_config_by_obj(apilist[i],data,factor_mt)
            if flag==False:
                self.interrupt_trade(id)
                return flag,errmsg

            #启动网格
            flag2,errmsg2,orderid=trader.start(factor_mt)
            if flag2==False:
                self.interrupt_trade(id)
                return flag2,errmsg2
            thread= threading.Thread(target=trader.order_monitor,args=(orderid,))
            thread.start()
            
            #初始化traders
            if id not in self.trades_map:
                self.trades_map[id]={}
                self.trades_map[id]['groupid']=groupid
                self.trades_map[id]['exchange']=exchange
                self.trades_map[id]['traders']=[]

            #将网格对象存入
            self.trades_map[id]['traders'].append({
                'trader':trader,
                'thread':thread
            })
        self.change_available_by_Ex_and_groupid(exchange,groupid,True)
        return True,'OK'
    
    def interrupt_trade(self,id):
        if id in self.trades_map:
            if 'traders' in self.trades_map[id]:
                count=len(self.trades_map[id]['traders'])
                for i in range(0,count):
                    self.trades_map[id]['traders'][i]['trader'].stop()
            del self.trades_map[id]
    
    def  grid_stop(self,data):
        id=data.get('id')
        if id==None:
            return http_response(STOP,'',-1,'参数错误')
        trade=self.trades_map.get(f'{id}')
        if trade==None:
            return http_response(STOP,id,-1,'该网格未开启')
        if 'traders' in trade:
            self.change_available_by_Ex_and_groupid(trade['exchange'],trade['groupid'],False)
            for index in range(0,len(trade['traders'])):
                trade['traders'][index]['trader'].stop()
        else:
            trade['trader'].stop()
            self.change_available_by_Ex_And_APIId(trade['exchange'],trade['apiid'],False)

        del self.trades_map[f'{id}']
        return http_response(STOP,id,0,'OK')

    def grid_update(self,data):
        id=data.get('key')
        json_data=data.get('content')
        
        #检查参数
        if id==None or json_data==None:
            return http_response(UPDATE,'',-1,'数据跟新失败,格式错误')

        #修改内存数据
        if id not in self.grids_map:
            title=''
            title1=data.get('title')
            if title1 !=None:
                title=title1
            self.grids_map[f'{id}']={
                'title':title,
                'content':json_data,
                'available':False,
            }
        else:
            self.grids_map[f'{id}']['content']=json_data
        
        #修改数据库数据
        flag,metadata=GridManager.metadata_encode(json_data)
        if flag==False:
            return http_response(UPDATE,id,-1,f'数据更新失败,格式错误')
        sql='update `tabs` set `metadata`=%s where `id`=%s'
        SqlHandler.Update(sql,[(metadata,id)])
        return http_response(UPDATE,id,0,'OK')

    def grid_del(self,data):
        id=data.get('key')
        if id in self.grids_map:
            #从缓存中删除
            del self.grids_map[f'{id}']

            #从数据库中删除
            sql= 'delete from `tabs` where id=%s'
            SqlHandler.Delete(sql,id)
        return http_response(DEL,id,0,'OK')

        

    def get_handler(self,path):     
        if len(path)==0:
            return http_response(INIT,'',-1,'请求数据格式错误')
            '''
            /api/calc?
            title=123&
            key=newTab1651074742690&
            content={"priceDecimal":6,"lotDecimal":6,"initialPrice":0,"maxPrice":0,"minPrice":0,"quantity":0,"stopPrice":0,"amount":0,"ratio":0}
            '''
        strs=path.split('?')
        count = len(strs)
        if count!=1 and count!=2 :
            return http_response(INIT,'',-1,'请求数据格式错误')
        else:
            if strs[0]==CALC:
                data=urldata_parse(strs[1])
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
        elif path==UPDATE:
            return self.grid_update(body)
        elif path==DEL:
            return self.grid_del(body)
        
        