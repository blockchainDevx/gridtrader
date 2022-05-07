import pymysql
from base64test import Encrption,Deode
import sys
import json

def insert(sql,data):
    try:
        connect=pymysql.Connect(host='18.162.245.242',user='root',password='gridtrade',database='grid_datas')
        cursor=connect.cursor(pymysql.cursors.DictCursor)
        res=cursor.execute(sql,data)
        connect.commit()
        cursor.close()
        connect.close()
    except Exception as e:
        print(str(e))

#参数: exchange,apikey,secret,password,subaccount
if __name__ == '__main__':
    count =len(sys.argv)
    if count < 4:
        print('参数错误,需要至少3个参数才能启动')
    # if len(sys.argv) > 1:
    exchange= sys.argv[1]
    apikey=sys.argv[2]
    secret=sys.argv[3]
    password=''
    if count>4 and sys.argv[4]!='-':
        password=sys.argv[4]
    subaccount=''
    if count>5 and sys.argv[5]!='-':
        subaccount=sys.argv[5]
    
    metadata={
        "ApiKey":apikey,
        "Secret":secret,
        "Password":password,
    }
    metastr=json.dumps(metadata)
    print(metastr)
    print(subaccount)
    print(exchange)
    metastr=Encrption(metastr)
    sql=f'insert into `api_datas` (metadata,marketplace,subaccount) values(%(metadata)s,%(marketplace)s,%(subaccount)s)'
    data={
        'metadata':metastr,
        'marketplace':exchange,
        'subaccount':subaccount
    }
    insert(sql,data)


    


        
        
