import asyncio
import aiomysql
import dbus
from ..configer.config import Config
from ..logger.Logger import Logger

__all__=['Query','Update']

async def query(sql,data={}):
    try:
        config=Config()
        chost=config.mysql['host']
        cport=config.mysql['port']
        cuser=config.mysql['user']
        cpasswd=config.mysql['password']
        cdtbase=config.mysql['database']
        connect=await aiomysql.connect(host=chost,port=cport,user=cuser,passwd=cpasswd,db=cdtbase)
        cursor=await connect.cursor(aiomysql.cursors.DictCursor)
        await cursor.execute(sql,data)
        result=cursor.fetchall()
        #print(res)
        await cursor.close()
        connect.close()
        return True,result
    except Exception as e:
        sstr=str(e)
        Logger().log('数据查询失败,{0},{1},错误为{2}'.format(sql,data,sstr))
        return False,None
    
async def update(sql,data={}):
    try:
        config=Config()
        chost=config.mysql['host']
        cport=config.mysql['port']
        cuser=config.mysql['user']
        cpasswd=config.mysql['password']
        cdtbase=config.mysql['database']
        connect=await aiomysql.connect(host=chost,port=cport,user=cuser,passwd=cpasswd,db=cdtbase)
        cursor= await connect.cursor(aiomysql.cursors.DictCursor)
        await cursor.executemany(sql,data)
        await connect.commit()
        await cursor.close()
        connect.close()
    except Exception as e:
        sstr=str(e)
        print(f'添加数据失败,{sql},{data},错误为{sstr}')
    
def Query(sql,data):
    return asyncio.run(query(sql,data))

def Update(sql,data):
    asyncio.run(update(sql,data))


