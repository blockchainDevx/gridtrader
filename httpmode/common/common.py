import json
import threading
import sys

from .ws.WebPush import WebPush
from .logger import Log

LOGIN='/api/login'
CALC='/api/calc'
START='/api/start'
STOP='/api/stop'
ADD='/api/add'
UPDATE='/api/change'
DEL='/api/del'
INIT='/api/tabs'
QUERY='/api/query'
ADDAPI='/api/addapi'
CHKST='/api/isstart'
GROUPS='/api/groups'
ADDAPIGROUP='/api/addapigroup'

SIGN_UT='/api/ut'
SIGN_STC_VALUE='/api/stc_value'
SIGN_STC_COLOR='/api/stc_color'

BUY_THRESHOLD=20
SELL_THRESHOLD=80

#结构元素名称
# TITL_UT='ut'
# TITL_STC_VALUE='stc_value'
# TITL_STC_COLOR='stc_color'

# TITL_SYMBOL='symbol'
# TITL_NUMBER='number'
# TITL_SIDE='side'
# TITL_GRIDTYPE='gridtype'
# TITL_SIGTP='signtype'
# TITL_SIG='sign'
# TITL_TR='trade'
# TITL_CON='content'
# TITL_TIL='title'
# TITL_ID='id'
# TITL_TIME='time'
# TITL_HOUR='hour'

WS_OPEN='wsconnect'
WS_PING='wsping'
WS_PONG='wspong'
WS_DATA='wsdata'
WS_SIGN='wssign'

#网格类型
COMM_GRID='1'
RAIS_GRID='2'
RAIS2_GRID='3'
SIGN_POLICY='4'

#买卖方向
BUY='buy'
SELL='sell'

#市价限价
MARKET='market'
LIMIT='limit'

#市场
OKEX='okex'
FTX='ftx'
BINANCE='binance'
GATE='gate'

#质押币个数
FTT_PLEDGE_QTY=25

#委托状态
ORDER_OPEN='open'
ORDER_CLOSED='closed'

SIGN_SECS={
    '15M':900,
    '30M':1800,
    '1H':3600,
    '2H':7200,
    '4H':14400,
}
#30天的秒数
A_MON_SEC=2592000



def obj_to_json(msgtype,errid,errmsg,data={},id=''):
        obj={
            'msgtype':msgtype,
            'id': id,
            'errid':errid,
            'errmsg':errmsg,
            'data':data}
        return json.dumps(obj)
    
def  urldata_parse(str):
    strs=str.split('&')
    data={}
    for i in range(0,len(strs)):
        eles=strs[i].split('=')
        if len(eles)==2:
            data[f'{eles[0]}']=eles[1]
    return data 


def http_response(msgtype,id,errid,errmsg,data={}):
    return json.dumps({
        'msgtype':msgtype,
        'id': id,
        'errid':errid,
        'errmsg':errmsg,
        'data':data
    })

#小数点保留位数,去尾
def Func_DecimalCut(f,n):
    return float(int(f*10**n)/10**n)

LOG_ALL=2
LOG_STORE=1
LOG_WS=0

def Record(msg,msgtype,level=3):
    if level == LOG_ALL:
        Log.log(msg)
        WebPush().sendmsg(msg,msgtype)
    elif level == LOG_STORE:
        print('log 1')
        Log.log(msg)
        print('log 2')
    elif level == LOG_WS:
        WebPush().sendmsg(msg,msgtype)