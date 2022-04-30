import base64
from pyDes import *
import chardet

#Des_Key = "W2*&@<FR" # Key 长度为8
Des_Key = "ilovejin" # Key 长度为8
#Des_IV = b"\x52\x63\x78\x61\xBC\x48\x6A\x07" # 自定IV向量
Des_IV = '*xiaoqi*' # 自定IV向量
 
 
# 加密
def Encrption(str):
    k = des(Des_Key, CBC, Des_IV, padmode=PAD_PKCS5)
    return base64.b64encode(k.encrypt(str))
 
# 解密
def Deode(str):
    k = des(Des_Key, CBC, Des_IV, padmode=PAD_PKCS5)
    return k.decrypt(base64.b64decode(str))


if __name__ == '__main__':
    #print(chardet.detect( Des_IV))
    d = Encrption("test pyDes")
    print(d)
    print(Encrption("my name is").decode("utf-8"))
    print(Deode(d))