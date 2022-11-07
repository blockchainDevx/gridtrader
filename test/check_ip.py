from time import time
import  requests
import json

__call__=['check_ip']

def check_ip(ip):
    try:
        url='https://whois.pconline.com.cn/ipJson.jsp?ip={0}&json=true'.format(ip)
        # print(url)
        res=requests.get(url=url,
                         timeout=5,
                         headers={'Content-type': 'text/plain; charset=utf-8'})
        data=res.json()
        return json.loads(json.dumps(data,ensure_ascii=False))
    except:
        return {}

if __name__ == '__main__':
    data=check_ip('49.51.71.60')
    print(data['pro'])
    print(data['addr'])
    print(data['region'])
    # print(json.dumps(text))
    # print(json.dumps(text).encode().decode("unicode_escape"))