import json
import threading

CALC='/api/calc'
START='/api/start'
STOP='/api/stop'
ADD='/api/add'
UPDATE='/api/change'
DEL='/api/del'
INIT='/api/tabs'
QUERY='/api/query'
ADDAPI='/api/addapi'
CHKST='/api/isstart'
GROUPS='/api/groups'
ADDAPIGROUP='/api/addapigroup'

#网格类型
COMM_GRID='1'
RAIS_GRID='2'

class Singleton():
    _instance_lock=threading.Lock()
    def __new__(cls,*args,**argv):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    orig=super(Singleton,cls)
                    cls._instance = orig.__new__(cls,*args,**argv)  
        return cls._instance

def obj_to_json(msgtype,errid,errmsg,data={},id=''):
        obj={
            'msgtype':msgtype,
            'id': id,
            'errid':errid,
            'errmsg':errmsg,
            'data':data}
        return json.dumps(obj)
    
def  urldata_parse(str):
    strs=str.split('&')
    data={}
    for i in range(0,len(strs)):
        eles=strs[i].split('=')
        if len(eles)==2:
            data[f'{eles[0]}']=eles[1]
    return data 

def http_response(msgtype,id,errid,errmsg,data={}):
    return json.dumps({
        'msgtype':msgtype,
        'id': id,
        'errid':errid,
        'errmsg':errmsg,
        'data':data
    })

#小数点保留位数,去尾
def Func_DecimalCut(f,n):
    return float(int(f*10**n)/10**n)