from pickletools import pyset
import pymysql
from config import Config

class SqlHandler():
    @staticmethod
    def Execute(sql,data={}):
        try:
            config= Config()
            chost=config.mysql['host']
            cport=config.mysql['port']
            cuser=config.mysql['user']
            cpasswd=config.mysql['password']
            cdtbase=config.mysql['database']
            connect= pymysql.Connect(host=chost,port=cport,user=cuser,passwd=cpasswd,database=cdtbase)
            cursor=connect.cursor(pymysql.cursors.DictCursor)
            res=cursor.execute(sql,data)
            result=cursor.fetchall()
            #print(res)
            cursor.close()
            connect.close()
            return True,res,result
        except:
            print(f'数据插入失败,{sql},{data}')
            return False,0,None
        
def GetAccounts():
    sql= 'select * from api_datas'
    
    