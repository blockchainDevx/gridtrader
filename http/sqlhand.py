from pickletools import pyset
import pymysql
from config import Config

class SqlHandler():
    @staticmethod
    def Query(sql,data={}):
        try:
            config=Config()
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
        except Exception as e:
            sstr=str(e)
            print(f'数据查询失败,{sql},{data},错误为{sstr}')
            return False,0,None
    
    @staticmethod
    def execute(sql,data):
        try:
            config=Config()
            chost=config.mysql['host']
            cport=config.mysql['port']
            cuser=config.mysql['user']
            cpasswd=config.mysql['password']
            cdtbase=config.mysql['database']
            connect= pymysql.Connect(host=chost,port=cport,user=cuser,passwd=cpasswd,database=cdtbase)
            cursor=connect.cursor(pymysql.cursors.DictCursor)
            cursor.execute(sql,data)
            connect.commit()
            cursor.close()
            connect.close()
        except Exception as e:
            sstr=str(e)
            print(f'添加数据失败,{sql},{data},错误为{sstr}')

    @staticmethod
    def Insert(sql,data):
        SqlHandler.execute(sql,data)

    @staticmethod
    def Delete(sql,data):
        SqlHandler.execute(sql,data)

    @staticmethod
    def Update(sql,data):
        try:
            config=Config()
            chost=config.mysql['host']
            cport=config.mysql['port']
            cuser=config.mysql['user']
            cpasswd=config.mysql['password']
            cdtbase=config.mysql['database']
            connect= pymysql.Connect(host=chost,port=cport,user=cuser,passwd=cpasswd,database=cdtbase)
            cursor=connect.cursor(pymysql.cursors.DictCursor)
            cursor.executemany(sql,data)
            connect.commit()
            cursor.close()
            connect.close()
        except Exception as e:
            sstr=str(e)
            print(f'添加数据失败,{sql},{data},错误为{sstr}')