#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import sys
import traceback

from common.redis import redis_util
from policies.SignPolicies.SignPolicy import SignPolicy

# from common.sendEmal import sendemail


sys.path.append('..')
from common.common import *
from policies.GridTraderHttp import GridTraderHttp 
from policies.HalfGridTraderHttp import HalfGridTrader
from policies.HalfGridVariantTraderHttp import HalfGridVariantTrader
from common.mysql.sqlhand import SqlHandler

from common.ip.check_ip import check_ip

from common.crypto.crypto import Encode,Decode
from common.redis import *
from common.single import Singleton

import time
import json

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
            'SymbolId': '', 
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
    def __init__(self) -> None:
        __grids_map={}
        __api_groups={}
        __trades_map={}
        __group_infos={}
        __symbol_tables=set()
        __lock=threading.Lock()

        sign={}
    
    @staticmethod
    def metadata_encode(metadata):
        try:
            str=json.dumps(metadata)
            return True, Encode(str)
        except Exception as e:
            msg=traceback.format_exc()
            print(msg)
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
            msg=traceback.format_exc()
            print(msg)
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
    
    #获取品种的信息
    def init_symbol_infos(self):
        r'''
        +----------+--------------+------+-----+---------+----------------+
        | id       | int unsigned | NO   | PRI | NULL    | auto_increment |
        | name     | varchar(40)  | NO   |     | NULL    |                |
        | exchange | varchar(40)  | NO   |     | NULL    |                |
        | qmin     | int          | NO   |     | NULL    |                |
        | qdigit   | int          | NO   |     | NULL    |                |
        | pmin     | int          | NO   |     | NULL    |                |
        | pdigit   | int          | NO   |     | NULL    |                |
        +----------+--------------+------+-----+---------+----------------+
        '''
        sql='select * from `symbol_tables`'
        flag,count,res=SqlHandler.Query(sql)
        if flag==True:
            for i in range(0,res):
                exchange=count[i]['exchange']
                symbol=count[i]['name']
                id=count[i]['id']
                qmin=int(count[i]['qmin'])
                qdigit=int(count[i]['qdigit'])
                pmin=int(count[i]['pmin'])
                pdigit=int(count[i]['pdigit'])
                self.__symbol_tables.add({
                    'id':id,
                    'exchange':exchange,
                    'symbol':symbol,
                    'qmin':qmin,
                    'qdigit':qdigit,
                    'pmin':pmin,
                    'pdigit':pdigit,
                })
        pass
        
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
            for i in range(0,len(res)):
                metadata=res[i].get('metadata')
                id=res[i].get('id')
                title=res[i].get('title')
                if metadata==None or id==None or title==None:
                    continue
                _,data=GridManager.metadata_decode(metadata)
                if data==None:
                    continue
                # print(str(data))
                self.__grids_map[f'{id}']={
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
            
            self.__group_infos[f'{id}']={
                'name':name,
                'exchange':exchange
            }

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
    
    #从redis中获取数据
    def get_signs(self):
        values= redis_util.keys()
         
        pass
    
    #api数据与组数据聚合
    def api_groups_compose(self,apis,groups):
        useable_list=[]
        for groupid,value in groups.items():
            exchange=value.get('exchange')
            
            exchanges=self.__api_groups.get(f'{exchange}')
            if exchanges == None:
                self.__api_groups[f'{exchange}']={}

            self.__api_groups[f'{exchange}'][f'{groupid}']={}
            #初始化时,group没有被使用
            self.__api_groups[f'{exchange}'][f'{groupid}']['available']=False

            apiid_arr=value.get('apiid_arr')
            if apiid_arr==None:
                continue
            for index in range(0,len(apiid_arr)):
                api_data=apis.get(f'{apiid_arr[index]}')
                if api_data==None:
                    continue

                #将API数据按照组分类
                if 'apilist' not in self.__api_groups[f'{exchange}'][f'{groupid}']:
                    self.__api_groups[f'{exchange}'][f'{groupid}']['apilist']=[]
                
                self.__api_groups[f'{exchange}'][f'{groupid}']['apilist'].append(
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
            meta1= self.__api_groups.get(f'{exchange}')
            if meta1==None:
                self.__api_groups[f'{exchange}']={}
            meta2=self.__api_groups[f'{exchange}'].get('-')
            if meta2==None:
                self.__api_groups[f'{exchange}']['-']=[]
            self.__api_groups[f'{exchange}']['-'].append({
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
            'GridType':'',
            'Exchange': '',
            'SymbolId': -1, 
            'Open': 0, 
            'UpBound': 0, 
            'LowBound': 0, 
            'RisRatio':0.0,
            'RetRatio':0.0,
            'GridQty': 0, 
            'Stop': 0, 
            'Amount': 0, 
            'Ratio':0,
            'GroupId':'-',
            'GroupList':[],
            'Qty':0,
            'SignType':'',
            'TPMode':TP_NONE,
            'TPFLTMode':TP_FLT_PER,
            'TPFLTPoint':0.0
        }
        self.__grids_map[f'{id}']={
                'title':title,
                'content':content
            }
        _,metadata=GridManager.metadata_encode(content)
        sql=f'insert into `tabs` (id,metadata,title) values(%(id)s,%(metadata)s,%(title)s)'
        data={'id':id,'metadata':metadata,'title':title}
        SqlHandler.Insert(sql,data)
        
    
    def get_API_by_exchange(self,exchange,groupid):
        exchange_map=self.__api_groups.get(f'{exchange}')
        if exchange_map==None:
            return False,f"根据交易所名称{exchange}没找到API组",None
        api_list=exchange_map.get(f'{groupid}')
        if api_list==None:
            return False,f"没有{exchange}的API",None
        if len(api_list)>0:
            api=api_list['apilist']
            return True,"OK",api[0]
        return False,f'没有{exchange}的API',None

    def get_useable_API_by_ex(self,exchange):
        exchange_map=self.__api_groups[f'{exchange}']
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
        if exchange in self.__api_groups:
            if '-' in self.__api_groups[f'{exchange}']:
                for index in range(0,len(self.__api_groups[f'{exchange}']['-'])):
                    if self.__api_groups[f'{exchange}']['-'][index]['ApiId']==apiid:
                        self.__api_groups[f'{exchange}']['-'][index]['available']=flag
    
    def change_available_by_Ex_and_groupid(self,exchange,groupid,flag):
        if exchange in self.__api_groups:
            if groupid in self.__api_groups[f'{exchange}']:
                self.__api_groups[f'{exchange}'][f'{groupid}']['available']=flag
    
    def update_tab_by_id(self,id,title,data):
        item=self.__grids_map.get(id)
        if item==None:
            self.__grids_map[f'{id}']={
                'title':title,
                'content':{
                    'GridType':data['GridType'],
                    'Exchange':data['Exchange'],
                    'SymbolId':data['SymbolId'],
                    'Open':data['Open'],
                    'UpBound':data['UpBound'],
                    'LowBound':data['LowBound'],
                    'RisRatio':data['RisRatio'],
                    'RetRatio':data['RetRatio'],
                    'GridQty':data['GridQty'],
                    'Stop':data['Stop'],
                    'Amount':data['Amount'],
                    'Ratio':data['Ratio'],
                    'GroupId':data['GroupId'],
                    'Slip':data['Slip'],
                    'GroupList':data.get('GroupList'),
                    'Qty':data.get('Qty'),
                    'SignType':data.get('SignType'),
                    'TPMode':data.get('TPMode'),
                    'TPFLTMode':data.get('TPFLTMode'),
                    'TPFLTPoint':data.get('TPFLTPoint'),
                }
            }                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
        else:
            item['title']=title
            item['content']['GridType']=data['GridType']
            item['content']['Exchange']=data['Exchange']
            item['content']['SymbolId']=data['SymbolId']
            item['content']['Open']=data['Open']
            item['content']['UpBound']=data['UpBound']
            item['content']['LowBound']=data['LowBound']
            item['content']['RisRatio']=data['RisRatio']
            item['content']['RetRatio']=data['RetRatio']
            item['content']['GridQty']=data['GridQty']
            item['content']['Stop']=data['Stop']
            item['content']['Amount']=data['Amount']
            item['content']['Ratio']=data['Ratio']
            item['content']['GroupId']=data['GroupId']
            item['content']['Slip']=data['Slip']
            item['content']['GroupList']=data.get('GroupList')
            item['content']['Qty']=data.get('Qty')
            item['content']['SignType']=data.get('SignType')
            item['content']['TPMode']=data.get('TPMode'),
            item['content']['TPFLTMode']=data.get('TPFLTMode'),
            item['content']['TPFLTPoint']=data.get('TPFLTPoint')

    def grid_init(self):
        data=[]
        for key,value in self.__grids_map.items():
            data.append({
                'key':key,
                'title':value['title'],
                'content':value['content']
            })
        return http_response(INIT,'',0,'OK',data)
    
    def get_groups(self):
        sql= 'select * from `group_infos`'
        flag,count,list=SqlHandler.Query(sql)
        if flag==False:
            return http_response(GROUPS,'',-1,'数据库获取不到组信息')

        data=[]
        for i in range(0,len(list)):
            id=list[i].get('groupid')
            name=list[i].get('groupname')
            exchange=list[i].get('exchange')
            data.append({
                'groupid':id,
                'groupname':name,
                'exchange':exchange
            })
        return http_response(GROUPS,'',0,'ok',data)
    
    #添加品种信息
    def add_symbol_info(self,data):
        if data== None or len(data)==None:
            return http_response(ADDSYMBOL,'',-1,'传输数据错误')
        
        try:
            
            doc_data=json.loads(data)
            if doc_data==None:
                return http_response(ADDSYMBOL,'',-1,'添加品种信息错误,传输的数据格式错误')
            if 'exchange' not in doc_data or \
                'symbol' not in doc_data or \
                'pmin' not in doc_data or \
                'qmin' not in doc_data:
                return http_response(ADDSYMBOL,'',-1,'添加品种信息错误,传输的数据有缺失')
            
            exchange=doc_data['exchange']
            symbol=doc_data['symbol']
            str_pmin=(doc_data['pmin'])
            str_qmin=(doc_data['qmin'])
            pdigit=get_decimal_places(str_pmin)
            qdigit=get_decimal_places(str_qmin)
            pmin=int(str_pmin*pdigit)
            qmin=int(str_qmin*qdigit)
            
            #添加数据库
            sql='insert into `symbol_tables` (`exchange`,`name`,`pmin`,`pdigit`,`qmin`,`qdigit`) values(%(exchange)s\
                ,%(name)s,%(pmin)s,%(pdigit)s,%(qmin)s,%qdigit))'
            data={'exchange':exchange,'name':symbol,'pmin':pmin,'pdigit':pdigit,'qmin':qmin,'qdigit':qdigit}
            id=SqlHandler.Insert(sql,data)
            if id==-1:
                return http_response(ADDSYMBOL,'',-1,'添加品种数据错误,数据库添加失败')
            self.__symbol_tables.add(
                {
                    'id':id,
                    'exchange':doc_data['exchange'],
                    'symbol':doc_data['symbol'],
                    'pmin':pmin,
                    'pdigit':pdigit,
                    'qmin':qmin,
                    'qdigit':qdigit
                }
            )
            
            return http_response(ADDSYMBOL,'',0,'OK',{'id':id})
        except:
            return http_response(ADDSYMBOL,'',-1,'添加品种信息错误,传输的数据格式错误')
        
        pass
    
    #通过交易所来获取该交易所支持的所有品种数据
    def get_symbols_by_ex(self,data):
        exchange=data.get('exchange')
        if exchange==None:
            return http_response(SYMBOLS,'',-1,'获取交易所品种失败,条件错误')
        symbols=None
        for i in range(0,len(self.__symbol_tables)):
            if exchange==self.__symbol_tables[i]['exchange']:
                symbols=self._symbol_tables[i]
                break
                
        if symbols ==None:
            return http_response(SYMBOLS,'',-1,'获取交易所品种数据失败,交易所不存在')
        else:
            symbollist=[]
            for i in range(0,len(symbols)):
                symbollist.appned({
                    'id':symbols[i]['id'],
                    'symbol':symbols[i]['symbol'],
                    'exchange':symbols[i]['exchange']
                })
            return http_response(SYMBOLS,'',0,'OK',symbollist)
            pass
        
    #通过ID删除品种数据
    def del_symbol_by_id(self,data):
        try:
            id=data.get('id')
            if id==None or len(id)==0:
                return http_response(DELSYMBOL,'',-1,'删除品种错误,没有传入ID')
            id=int(id)
            for i in range(0,len(self.__symbol_tables)):
                if id== self.__symbol_tables[i]['id']:
                    del self.__symbol_tables[i]
                    
        except:
            msg=traceback.format_exc()
            Record(msg,level=LOG_STORE)
    
    @staticmethod
    def del_symbol_from_db_by_id(id):
        try:
            sql='del * from `symbol_tables` where `id`=%s'
            SqlHandler.Delete(sql,id)
        except:
            msg=traceback.format_exc()
            Record(msg,level=LOG_STORE)
        
    def get_symbol_by_id(self,id):
        if id == None or id <0:
            return None
        for i in range(0,len(self.__symbol_tables)):
            if id== self.__symbol_tables[i]['id']:
                return  self.__symbol_tables[i]
        return None

    def check_start(self,data):
        id= data.get('id')
        if id== None:
            return http_response(CHKST,'',-1,'参数不对')

        #检查组是否已启用
        if id in self.__trades_map:
            return http_response(CHKST,id,1,'网格已经开启,不能关闭')
        else:
            return http_response(CHKST,id,0,'OK')

    def login_record(self,data,clientip):
        # print(json.dumps(data))
        ipdata=check_ip(clientip)
        
        #屏蔽发邮件
        # try:
        #     if ipdata== None:
        #         sendemail('账号 {0} 登录,时间: {1}, IP信息: {2}'.format(data['account'],data['time'],clientip))
        #     else:
        #         city=ipdata.get('city')
        #         region=ipdata.get('region')
        #         addr=ipdata.get('addr')
        #         msg1='IP地址: {0},所属城市:{1},地区:{2},地址:{3}'.format(clientip,city,region,addr)
        #         msg= '账号 {0} 登录,时间: {1}, IP信息: {2} '.format(data['account'],data['time'],msg1)
        #         sendemail(msg)
        #     pass
        # except:
        #     pass
        
        return http_response(LOGIN,'',0,'OK')
    
    '''
        ut信号格式:{
            sign:'UT',
            side:'buy',
            price:'17000',
            close:'16000',
            time:1662308649859,
            hour:1,
        }
    '''
    def sign_ut(self,data):
        if data==None:
            return
        symbol=data.get('symbol')
        sign=data.get('sign')
        side=data.get('side')
        price=data.get('price')
        time=data.get('time')
        hour=data.get('hour')
        if symbol==None or sign==None or side==None or price==None or time==None or hour==None:
            Record(f'ut数据错误,{json.dumps(data)}',level=LOG_STORE)
            return
        
        if symbol not in self.sign:
                self.sign[symbol]={}
            
        if hour not in self.sign[symbol]:
            self.sign[symbol][hour]={}
            self.sign[symbol][hour]['ut']={}
        self.sign[symbol][hour]['ut']={
            'side':side,
            'price':price,
            'time':time
        }

        self.sign_handle(symbol,hour)
        # msg= json.dumps(data)
        # Record(msg,WS_SIGN,LOG_WS)
        pass

    '''
        stc_value信号格式
        {
            sign:'STC_VALUE',
            number:20,
            price:'17000',
            time:1662308649859,
            hour:1
        }
    '''
    def sign_stc_value(self,data):
        if data == None:
            return
        symbol=data.get('symbol')
        sign=data.get('sign')
        number=int(data.get('number'))
        time=data.get('time')
        hour=data.get('hour')
        if symbol==None or sign==None or number==None or time==None or hour==None:
            Record(f'value数据错误,{json.dumps(data)}',level=LOG_STORE)
            return
        
        try: 
            if symbol not in self.sign:
                self.sign[symbol]={}
            
            if hour not in self.sign[symbol]:
                self.sign[symbol][hour]={}
                self.sign[symbol][hour]['stc_value']={}
                
            self.sign[symbol][hour]['stc_value']={
                'number':number,
                'time':time,
            }
        except Exception as e:
            msg=traceback.format_exc()
            Record(f'value 数据异常, {msg}',level=LOG_STORE)
            return
        self.sign_handle(symbol,hour)
        # msg= json.dumps(data)
        # Record(msg,WS_SIGN,LOG_WS)

        pass

    '''
        stc_color信号格式
        {
            sign:'STC_COLOR',
            side:'sell',
            price:'17000',
            time:1662308649859,
            hour:1
        }
    '''
    def sign_stc_color(self,data):
        if data== None:
            return
        symbol=data.get('symbol')
        sign=data.get('sign')
        side=data.get('side')
        time=data.get('time')
        hour=data.get('hour')

        if symbol==None or sign==None or side==None or time==None or hour==None:
            Record(f'color 数据错误,{json.dumps(data)}',level=LOG_STORE)
            return
        
        if symbol not in self.sign:
                self.sign[symbol]={}
        if hour not in self.sign[symbol]:
            self.sign[symbol][hour]={}
            self.sign[symbol][hour]['stc_color']={}
        self.sign[symbol][hour]['stc_color']={
            'side':side,
            'time':time,
        }

        self.sign_handle(symbol,hour)
        # msg= json.dumps(data)
        # Record(msg,WS_SIGN,LOG_WS)
        pass

    def sign_handle(self,symbol,hour):
        #检测数据是否存在
        if symbol not in self.sign or hour not in self.sign[symbol]:
            return
        
        #检测三种信号是否都存在
        if 'ut' not in self.sign[symbol][hour] or \
           'stc_value' not in self.sign[symbol][hour] or\
           'stc_color' not in self.sign[symbol][hour]:
           return

        ut=self.sign[symbol][hour]['ut']
        stc_value=self.sign[symbol][hour]['stc_value']
        stc_color=self.sign[symbol][hour]['stc_color']
        side=''
        if stc_value['number']==BUY_THRESHOLD and ut['side']==BUY and stc_color['side']==BUY: #买信号
            side=BUY
            pass
        elif stc_value['number']==SELL_THRESHOLD and ut['side']==SELL and stc_color['side']==SELL: #卖信号
            side=SELL
            pass
        else:
            return
        
        now=time.time()
        for item in self.__trades_map.values():
            if item['gridtype']==SIGN_POLICY and item['symbol']==symbol and item['signtype']==hour:
                #每次触发信号有时间间隔,如果在间隔没,不做处理
                if 'time' not in self.sign[symbol][hour] or int(now -self.sign[symbol][hour]['time'])>SIGN_SECS[hour]:
                    item['trade'].create_order(side)
                    self.sign[symbol][hour]['time']=int(now)    #记录触发的时间戳
                pass
        #将历史信号存入redis,30天后自动删除
        key='hs:{0}:{1}:{2}:{3}'.format(symbol,hour,int(now),side)
        redis_util.set(key,'',expire=A_MON_SEC)
        
        return
            
    def grid_calc(self,data):
        content= data.get('content')  
        title=data.get('title')
        id=data.get('key')
        if content==None or id==None or title==None:
            return  http_response(CALC,'', -1,'数据格式错误')
        try:
            json_data=json.loads(content)
            grid_type=json_data.get('GridType')
            if grid_type==None:
                return http_response(CALC,'',-1,'没有发现网格类型')
            
            err_msg=''
            if grid_type==COMM_GRID:
                flag,err_msg=GridTraderHttp.parms_check(json_data)
            elif grid_type==RAIS_GRID:
                flag,err_msg=HalfGridTrader.parms_check(json_data)
            elif grid_type==RAIS2_GRID:
                flag,err_msg=HalfGridVariantTrader.parms_check(json_data)
            else:
                return http_response(CALC,id,-1,'网格类型不支持')

            if flag==False:
                return http_response(CALC,id,-1,err_msg)
            
             #根据配置中的exchange获取第一份api数据
            flag,err_msg,api=self.get_API_by_exchange(json_data['Exchange'],json_data['GroupId'])
            if flag==False:
                return http_response(CALC,id,-1,err_msg)
            
            #计算数据
            if grid_type==COMM_GRID:
                flag,err_msg,data1=GridTraderHttp.grid_calc(api,json_data)
            elif grid_type==RAIS_GRID:
                flag,err_msg,data1=HalfGridTrader.grid_calc(api,json_data)
            elif grid_type==RAIS2_GRID:
                flag,err_msg,data1=HalfGridVariantTrader.grid_calc(api,json_data)
            else:
                return http_response(CALC,id,-1,'网格类型不支持')

            if flag==False:
                return http_response(CALC,id,-1,err_msg)
            
            #参数检测完之后更新缓存中的数据
            self.update_tab_by_id(id,title,json_data)
            
            return http_response(CALC,id,0,err_msg,data1)
        except Exception as e:
            msg=traceback.format_exc()
            Record(f'计算发生错误,{msg}')
            return  http_response(CALC,id,-1,'计算数据格式错误')

    def grid_start(self,data):
        id=data.get('id')
        if id==None:
            return http_response(START,'',-1,'网格开启错误,参数错误')
        
        #检查组是否已启用
        if id in self.__trades_map:
            return http_response(START,id,-1,'网格开启错误,网格已经开启')
        
        #根据传入的key查找网格配置数据
        conf_data=self.__grids_map.get(id)
        if conf_data==None: #没找到数据,返回错误
            return http_response(START,id,-1,'网格开启错误,未根据页面编号找到网格数据')
        
        if(conf_data['content']['GridType']==SIGN_POLICY):
            return self.create_trades(id,conf_data['content'],conf_data['title'])
        else:
            #根据组ID与交易所名称找到API数据数组
            exchange= conf_data['content']['Exchange']
            groupid=str(conf_data['content']['GroupId'])
            if exchange not in self.__api_groups or groupid not in self.__api_groups[f'{exchange}']:
                return http_response(START,id,-1,'网格开启错误,根据组与交易所未找到账号API数据')

            if self.__api_groups[f'{exchange}'][f'{groupid}']['available']==True:
                return http_response(START,id,-1,'网格开启错误,网格配置的API组已被占用')

            apilist=self.__api_groups[f'{exchange}'][f'{groupid}']['apilist']
            api_count=len(apilist)
            if api_count==0:
                return http_response(START,id,-1,'网格开启错误,根据组与交易所未找到账号API数据')
            elif api_count==1:#如果API数组里数据只有一个
                return self.create_trade(apilist[0],id,conf_data['content'])
    
    def create_trade(self,api,id,data):
        #创建网格
        trader={}
        if data['GridType']==COMM_GRID:
            trader=GridTraderHttp()
        elif data['GridType']==RAIS_GRID:
            trader=HalfGridTrader()
        elif data['GridType']==RAIS2_GRID:
            trader=HalfGridVariantTrader()
        else:
            return http_response(START,id,-1,'网格类型错误')

        flag,errmsg=trader.read_config_by_obj(api,data)
        if flag==False:
            return http_response(START,id,-1,errmsg)
        
        #启动网格
        flag2,errmsg2,orderid=trader.start()
        if flag2==False:
            return http_response(START,id,-1,errmsg2)
        trader.create_monitor(orderid,self.__lock)

        #将网格对象数据保存
        self.__trades_map[id]={
            'trader':trader,
            'gridtype':data['GridType'],
            'exchange':data['Exchange'],
            'groupid':data['GroupId']
            }

        #将API状态设置为已启用
        self.change_available_by_Ex_and_groupid(data['Exchange'],data['GroupId'],True)
        return http_response(START,id,0,'OK')

    #信号策略专用
    def create_trades(self,id,data,title):
        
        groupidlist=data['GroupList']
        signtype=data['SignType']
        qty=int(data['Qty'])
        symbol_id=data['SymbolId']
        stop=float(data['Stop'])
        tp_mode=data['TPMode']
        
        symbol_info=self.get_symbol_by_id(symbol_id)
        if symbol_info==None:
            return http_response(START,id,-1,f'品种选择错误,没有这个品种')
        
        symbol=symbol_info['symbol']
        strs= symbol.split('/')
        if len(strs)!=2:
            return http_response(START,id,-1,f'品种格式不对{symbol}')
        
        #批量启动数据
        params={
            'symbol':symbol,
            'keyName': title,
            'qmin':symbol_info['qmin'],
            'qdigit':symbol_info['qdigit'],
            'signType':signtype,
            'qty':qty,
            'tpMode':tp_mode,
        }
        
        #止损配置
        if stop != 0.0:
            params['pmin']=symbol_info['pmin']
            params['pdigit']=symbol_info['pdigit']
            params['stopPer']=stop
            
        #止盈配置
        if tp_mode ==TP_FLOATING:
            params['fltMode']= data['TPFLTMode']
            params['fltPoint']=data['TPFLTPoint']
            
        trade=SignPolicy()
        flag=trade.init(params)
        if flag == False:
            return http_response(START,id,-1,'信号策略数据错误,止盈百分比设置值大于1')
        apilist=[]
        for i in range(0,len(groupidlist)):
            groupid = groupidlist[i]
            group=self.__group_infos.get(f'{groupid}')
            if group==None:
                continue
            if self.__api_groups[group['exchange']][f'{groupid}']['available']==True:
                #这个API已经被使用了
                continue
            
            apilist.append({
                'GroupName':group['name'],
                'Exchange':group['exchange'],
                'Content':self.__api_groups[group['exchange']][f'{groupid}']['apilist'][0]
            })
            #不需要将API标记已使用,信号策略和网格策略不一样不用单独使用
            #将API标记为已使用,
            # self.change_available_by_Ex_and_groupid(exchange,groupid,True)
            
        
        trade.start(apilist)
        
        new_symbol=strs[0]+strs[1]
        trd_data={
            'trade':trade,
            'gridtype':SIGN_POLICY,
            'symbol':new_symbol,
            'signtype':signtype
        }
        self.__trades_map[id]=trd_data
        return http_response(START,id,0,'OK')
    
    def interrupt_trade(self,id):
        if id in self.__trades_map:
            if 'trader' in self.__trades_map[id]:
                count=len(self.__trades_map[id]['trader'])
                for i in range(0,count):
                    self.__trades_map[id]['trader'][i]['trader'].stop()
            del self.__trades_map[id]
    
    def grid_stop(self,data):
        id=data.get('id')
        if id==None:
            return http_response(STOP,'',-1,'参数错误')
        gridobj=self.__trades_map.get(f'{id}')
        if gridobj==None:
            return http_response(STOP,id,-1,'该网格未开启')
        gridobj['trade'].stop()
        if gridobj['gridtype']!=SIGN_POLICY:
            self.change_available_by_Ex_and_groupid(gridobj['exchange'],gridobj['groupid'],False)

        # if 'traders' in gridobj:
        #     self.change_available_by_Ex_and_groupid(gridobj['exchange'],gridobj['groupid'],False)
        #     for index in range(0,len(gridobj['traders'])):
        #         gridobj['traders'][index]['trader'].stop()
        # else:
        #     gridobj['trader'].stop()
        #     self.change_available_by_Ex_and_groupid(gridobj['exchange'],gridobj['groupid'],False)
        del self.__trades_map[f'{id}']
        return http_response(STOP,id,0,'OK')

    def grid_update(self,data):
        id=data.get('key')
        json_data=data.get('content')
        
        #检查参数
        if id==None or json_data==None:
            return http_response(UPDATE,'',-1,'数据跟新失败,格式错误')

        #修改内存数据
        if id not in self.__grids_map:
            title=''
            title1=data.get('title')
            if title1 !=None:
                title=title1
            self.__grids_map[f'{id}']={
                'title':title,
                'content':json_data,
                'available':False,
            }
        else:
            self.__grids_map[f'{id}']['content']=json_data
        
        #修改数据库数据
        flag,metadata=GridManager.metadata_encode(json_data)
        if flag==False:
            return http_response(UPDATE,id,-1,f'数据更新失败,格式错误')
        sql='update `tabs` set `metadata`=%s where `id`=%s'
        SqlHandler.Update(sql,[(metadata,id)])
        return http_response(UPDATE,id,0,'OK')

    def grid_del(self,data):
        id=data.get('key')
        if id in self.__grids_map:
            #从缓存中删除
            del self.__grids_map[f'{id}']

            #从数据库中删除
            sql= 'delete from `tabs` where id=%s'
            SqlHandler.Delete(sql,id)
        return http_response(DEL,id,0,'OK')


    #用小程序将API数据和group数据存入,然后调用接口将数据从数据库中查出来,然后将api与group配对
    def add_api(self,data)  :
        apiid=data.get('apiid')
        groupid=data.get('groupid')
        if apiid==None or groupid==None:
            return http_response(ADDAPI,'',-1,'API添加错误,添加的数据不全')
        
        sql='select * from `api_datas` where `id`=%(id)s' 
        flag1,_,api_data=SqlHandler.Query(sql,{'id':apiid})

        sql2= 'select * from `group_infos` where `groupid` =%(groupid)s'
        flag2,_,group_info=SqlHandler.Query(sql2,{'groupid':groupid})
        if flag1==False or flag2==False:
            return http_response(ADDAPI,'',-1,'API添加错误,根据提供的API或Group未找到数据')

        metadata=api_data[0].get('metadata')
        id=api_data[0].get('id')
        marketpalce=api_data[0].get('marketplace')
        subaccount=api_data[0].get('subaccount')
        if metadata==None or id ==None or marketpalce==None:
            return http_response(ADDAPI,'',-1,'API添加错误,数据库里查出的数据缺失')
        _,apidata=GridManager.metadata_decode(metadata)
        if apidata==None:
            return http_response(ADDAPI,'',-1,'API添加错误,数据库里的数据加密格式错误')

        exchange1=group_info[0]['exchange']
        exchange2=api_data[0]['marketplace']
        if exchange1 != exchange2:
            return http_response(ADDAPI,'',-1,'API添加数据,API数据支持的交易所跟组配置的交易所不匹配')
        with self.__lock:
            if f'{groupid}' in self.__api_groups[f'{exchange1}']:
                self.__api_groups[f'{exchange1}'][f'{groupid}']['apilist'].append({
                    'ApiId': apiid,
                    'Exchange':marketpalce,
                    'API':apidata,
                    'Subaccount':subaccount
                })
            else:
                self.__api_groups[f'{exchange1}'][f'{exchange1}']={}
                self.__api_groups[f'{exchange1}'][f'{exchange1}']['available']=False
                self.__api_groups[f'{exchange1}'][f'{exchange1}']['apilist']=[]
                self.__api_groups[f'{exchange1}'][f'{exchange1}']['apilist'].append({
                    'ApiId': apiid,
                    'Exchange':marketpalce,
                    'API':apidata,
                    'Subaccount':subaccount
                })
        
        #将配对数据加入数据库
        sql=f'insert into `groups` (groupid,apiid) values(%(groupid)s,%(apiid)s)'
        data={
            'groupid':groupid,
            'apiid':apiid
        }
        SqlHandler.Insert(sql,data)
        return http_response(ADDAPI,'',0,'OK')         

    #将组与apiid绑定
    def bind_api_group(self,data):
        api_id=0
        try:
            api_id=int(data.get('apiId'))
        except Exception as e:
            return http_response(ADDAPIGROUP,'',-1,'传入参数不对')

        group_name=data.get('groupName')
        if api_id==None or group_name==None:
            return http_response(ADDAPIGROUP,'',-1,'传入参数不对')
        sql='select * from `api_datas` where `id`=%(id)s'
        data={
            'id':api_id
        }
        flag,count,list=SqlHandler.Query(sql,data)
        if flag==None or count==0:
            return http_response(ADDAPIGROUP,'',-1,'根据传入的APIId没有找到API数据')
        sql2='select * from `group_infos` where `groupname`=%(groupname)s'
        data2={
            'groupname':group_name
        }
        flag2,count2,list2=SqlHandler.Query(sql2,data2)
        if count2==0:
            #根据groupname没在数据库中找到group数据
            pk=SqlHandler.Insert('insert into `group_infos` (groupname,exchange) values(%(groupname)s,%(exchange)s)',{
                'groupname':group_name,
                'exchange':list[0]['marketplace']
            })
            if pk==-1:
                return http_response(ADDAPIGROUP,'',-1,'数据插入失败')
            
            #将group与api配对写入数据库
            ret=SqlHandler.Insert('insert into `groups` (apiid,groupid) values(%(apiid)s,%(groupid)s)',{
                'apiid':api_id,
                'groupid':int(pk)
            })
            if ret==-1:
                return http_response(ADDAPIGROUP,'',-1,'数据插入失败')
        else:
            #数据库里有数据
            ret=SqlHandler.Insert('insert into `groups` (apiid,groupid) values(%(apiid)s,%(groupid)s)',{
                'apiid':int(api_id),
                'groupid':int(list2[0]['groupid'])
            })
            if ret==-1:
                return http_response(ADDAPIGROUP,'',-1,'数据插入失败')
        return http_response(ADDAPIGROUP,'',0,'OK',{'groupid':pk,'groupname':group_name,'exchange':list[0]['marketplace']})
        pass

    def get_handler(self,path,clientip):     
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
            elif strs[0]==GROUPS:
                return self.get_groups()
            elif strs[0]==SYMBOLS:
                return self.get_symbols_by_ex(strs[1])
            elif strs[0]==CHKST:
                data=urldata_parse(strs[1])
                return self.check_start(data)
            elif strs[0]==LOGIN:
                data=urldata_parse(strs[1])
                return self.login_record(data,clientip)
               
    def post_handler(self,path,body):
        if path not in  (SIGN_UT,SIGN_STC_COLOR,SIGN_STC_VALUE):
           Record( 'POST:{0},{1}'.format(path,body),None,LOG_STORE)
        try:
            
            if path==ADD:
                data = json.loads(body)
                return self.grid_add(data)
            elif path==START:
                data = json.loads(body)
                return self.grid_start(data)
            elif path==STOP:
                data = json.loads(body)
                return self.grid_stop(data)
            elif path==UPDATE:
                data = json.loads(body)
                return self.grid_update(data)
            elif path==DEL:
                data = json.loads(body)
                return self.grid_del(data)
            elif path==ADDAPI:
                data = json.loads(body)
                return self.add_api(data)
            elif path==ADDAPIGROUP:
                data = json.loads(body)
                return self.bind_api_group(data)
            elif path==ADDSYMBOL:
                data=json.loads(body)
                return self.add_symbol_info(data)
            elif path==DELSYMBOL:
                data=json.loads(body)
                return self.del_symbol_by_id(data)
            elif path==SIGN_UT:
                data= self.ut_loads(body)
                return  self.sign_ut(data)
            elif path==SIGN_STC_VALUE:
                data=self.value_loads(body)
                return  self.sign_stc_value(data)
            elif path==SIGN_STC_COLOR:
                data=self.color_loads(body)
                return  self.sign_stc_color(data)
            else:
                pass
        except:
            msg=traceback.format_exc()
            return http_response(path,'',-1,msg)
    
    
    def ut_loads(self,body):  
        body=str(body)
        body=body.split('\'')[1]
        strs=body.split(',')
        if len(strs)==6:
            data={
                'sign':str(strs[0]),
                'side':strs[1],
                'symbol':strs[2],
                'price':strs[3],
                'time':strs[4],
                'hour':strs[5]
            }
            return data
        return None        

    def value_loads(self,body):
        body=str(body)
        body=body.split('\'')[1]
        strs=body.split(',')
        if len(strs)==5:
            data={
                'sign':str(strs[0]),
                'number':int(strs[1]),
                'symbol':strs[2],
                'time':strs[3],
                'hour':strs[4]
            }
            return data
        return None
    
    def color_loads(self,body):
        body=str(body)
        body=body.split('\'')[1]
        strs=body.split(',')
        if len(strs) == 5:
            data={
                'sign':str(strs[0]),
                'side':strs[1],
                'symbol':strs[2],
                'time':strs[3],
                'hour':strs[4]
            }
            return data
        return None