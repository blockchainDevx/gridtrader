import redis

__all__=['get','set']

def redis_client():
    rs=redis.StrictRedis(host='localhost',port=6379)
    return rs

def redis_close(rs):
    if rs!=None:
        rs.close()

def set(key,value,expire=0):
    rs=redis_client()
    rs.set(key,value,expire)
    redis_close(rs)

def get(key):
    rs=redis_client()
    value=rs.get(key)
    redis_close(rs)
    return value.decode('utf-8')
    
def keys():
    rs=redis_client()
    values=rs.keys('*')
    redis_close()
    values2=set()
    for value in values:
        values2.append(value.decode('utf-8'))
    return values2