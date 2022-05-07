import base64
from pyDes import *

def Encode(str,key='gridtrad',iv='*xiaoqi*'):
    k = des(key,CBC,iv, padmode=PAD_PKCS5)
    return base64.b64encode(k.encrypt(str))
 
# 解密
def Decode(str,key='gridtrad',iv='*xiaoqi*'):
    k = des(key,CBC, iv, padmode=PAD_PKCS5)
    return k.decrypt(base64.b64decode(str))