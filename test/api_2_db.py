from tokenize import group
import pymysql
from base64test import Encrption,Deode
import sys
import json

def insert(sql,data):
    try:
        # connect=pymysql.Connect(host='18.162.245.242',user='root',password='gridtrade',database='grid_datas')
        connect=pymysql.Connect(host='127.0.0.1',user='root',password='gridtrade',database='grid_datas')
        cursor=connect.cursor(pymysql.cursors.DictCursor)
        res=cursor.execute(sql,data)
        id=connect.insert_id()
        ret=connect.commit()
        cursor.close()
        connect.close()
        return True,id
    except Exception as e:
        print(str(e))
        return False,None

#参数: exchange,apikey,secret,password,subaccount
if __name__ == '__main__':
    count =len(sys.argv)
    if count < 4:
        print('参数错误,需要至少3个参数才能启动')
    # if len(sys.argv) > 1:
    exchange1= sys.argv[1]
    apikey=sys.argv[2]
    secret=sys.argv[3]
    password=''
    if count>4 and sys.argv[4]!='-':
        password=sys.argv[4]
    subaccount=''
    if count>5 and sys.argv[5]!='-':
        subaccount=sys.argv[5]
    
    # groupname1=''
    # if count>6 and sys.argv[6]!='-':
    #     try:
    #         groupname1=sys.argv[6]
    #     except Exception as e:
    #         print('groupid错误:'+str(e))

    metadata={
        "ApiKey":apikey,
        "Secret":secret,
        "Password":password,
    }
    metastr=json.dumps(metadata)
    print(metastr)
    print(subaccount)
    print(exchange1)
    metastr=Encrption(metastr)
    sql=f'insert into `api_datas` (metadata,marketplace,subaccount) values(%(metadata)s,%(marketplace)s,%(subaccount)s)'
    data={
        'metadata':metastr,
        'marketplace':exchange1,
        'subaccount':subaccount
    }
    flag,ret=insert(sql,data)
    print(f'apiid:{ret}')

    # sql2=f'insert into `group_infos` (groupname,exchange) values(%(groupname)s,%(exchange)s)'
    # data2={
    #     'groupname': groupname1,
    #     'exchange':exchange1
    # }
    # flag,ret2=insert(sql2,data2)
    # print(f'apiid:{ret},groupid:{ret2}')
    # if flag==True and groupid!=-1:
    #     sql=f'insert into `groups` (groupid,apiid) values(%(groupid)s,%(apiid)s)'
    #     data={
    #         'groupid':groupid,
    #         'apiid':ret
    #     }
    #     insert(sql,data) 


    


        
        
