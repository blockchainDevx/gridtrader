from common.mysql.sqlhand import SqlHandler
from common.crypto.crypto import Encode,Decode

import json
import traceback

class DataMgr():
    def __init__(self):
        __grids_map={}
        __api_groups={}
        __group_infos={}
        pass
    
    #获取API账号
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
                _,data=DataMgr.metadata_decode(metadata)
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
    
    #获取网页数据    
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
                _,data=DataMgr.metadata_decode(metadata)
                if data==None:
                    continue
                # print(str(data))
                self.__grids_map[f'{id}']={
                    'title':title,
                    'content':data,
                    'available':False,
                }

    #获取组数据
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
    
    def  grid_db_update(self,str):
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
                    'Symbol':data['Symbol'],
                    'PriceReserve':data['PriceReserve'],
                    'QtyReserve':data['QtyReserve'],
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
            item['content']['Symbol']=data['Symbol']
            item['content']['PriceReserve']=data['PriceReserve']
            item['content']['QtyReserve']=data['QtyReserve']
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

    def grid_add(self,data):
        title=data.get('title')
        key=data.get('key')
        if title==None or key == None:
            return http_response(ADD,'',-1,'添加网格配置表失败')
        else:
            self.add_grid_data(key,title)
            return http_response(ADD,f'{key}',0,'ok')
    
    @staticmethod
    def metadata_encode(metadata):
        try:
            str=json.dumps(metadata)
            return True, Encode(str)
        except Exception as e:
            msg=traceback.format_exc()
            print(msg)
            return False,None
        
    def  get_grid_by_id(self,id):
        return self.__grids_map.get(id)
        pass
    
    def get_apis_by_ex_and_groupid(self,exchange,groupid):
        if exchange not in self.__api_groups or groupid not in self.__api_groups[f'{exchange}']:
                return http_response(START,id,-1,'网格开启错误,根据组与交易所未找到账号API数据')

        if self.__api_groups[f'{exchange}'][f'{groupid}']['available']==True:
            return http_response(START,id,-1,'网格开启错误,网格配置的API组已被占用')

        apilist=self.__api_groups[f'{exchange}'][f'{groupid}']['apilist']
        return apilist
    
    def add_grid(self,id,title,content):
        self.__grids_map[f'{id}']={
                'title':title,
                'content':content
            }
        _,metadata=DataMgr.metadata_encode(content)
        sql=f'insert into `tabs` (id,metadata,title) values(%(id)s,%(metadata)s,%(title)s)'
        data={'id':id,'metadata':metadata,'title':title}
        SqlHandler.Insert(sql,data)
    
    #获取组信息
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
    
    def grid_update(self,id,json_data):
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
        pass
    
    def grid_del(self,id):
        if id in self.__grids_map:
                #从缓存中删除
            del self.__grids_map[f'{id}']

            #从数据库中删除
            sql= 'delete from `tabs` where id=%s'
            SqlHandler.Delete(sql,id)
        return http_response(DEL,id,0,'OK')

    def add_api(self,apiid,groupid):
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

    def bind_api_group(self,apiid,groupname):
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