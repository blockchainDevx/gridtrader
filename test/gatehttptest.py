# coding: utf-8
import requests
import time
import hashlib
import hmac

def gen_sign(method, url, query_string=None, payload_string=None):
    key = 'cc2530771c1e788d4c38027ce9543a2e'        # api_key
    secret = '696ce9ec9e4834a40f95d9cf05f312bb54388184d3306e7b8165ade575a1f38c'     # api_secret

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

host = "https://api.gateio.ws"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

url = '/futures/usdt/orders'
query_param = ''
body='{"contract":"ETH_USDT","size":1,"iceberg":0}'
# `gen_sign` 的实现参考认证一章
sign_headers = gen_sign('POST', prefix + url, query_param, body)
headers.update(sign_headers)
r = requests.request('POST', host + prefix + url, headers=headers, data=body)
print(r.json())