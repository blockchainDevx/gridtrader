import json

CALC='/api/calc'
START='/api/start'
ADD='/api/add'
STOP='/api/stop'

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
    return json.dump({
        'msgtype':msgtype,
        'id': id,
        'errid':errid,
        'errmsg':errmsg,
        'data':data
    })