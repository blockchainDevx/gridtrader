import  requests
import json

__all__=['check_ip']

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