import redis
import time

st=time.time()
rs=redis.StrictRedis(host='localhost',port=6379,db=0)
# rs.set(name='test1',value='123',ex=10)
ed=time.time()
# print(f'{ed-st}')
# value=rs.get('test1')
# print(value if value!=None else 'nil')
# time.sleep(11)
# value=rs.get('test1')
# print(value if value!=None else 'nil')

values=rs.keys('*')
print(values if values!=None else 'nil')
for item in values:
    print(item.decode('utf-8'))

value=rs.get('key1')
print(value)