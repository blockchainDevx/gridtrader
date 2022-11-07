import asyncio
import aiomysql
import time

async def execute1():
    conn= await aiomysql.connect(host='localhost',user='root',password='gridtrade',db='grid_datas')
    cur = await conn.cursor()
    await cur.execute('select * from api_datas')
    result = await cur.fetchall(aiomysql.cursors.DictCursor)
    return result
    await cur.close()
    conn.close()
    
print(time.time())    
result=asyncio.run(execute1())
print(f'\tresult :{result}')
print(time.time())
