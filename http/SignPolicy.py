from CommonGridTrader import *
from TraderAPI import TraderAPI
from common import *
from WebPush import WebPush

class SignPolicy(IGridTrader):
    __apis=set()
    __qty=0.0

    def __init__(self,qty):
        self.__qty=qty


    #网格开始
    def start(self,apilist):
        for item in apilist:
            
            tradehd=TraderAPI(item['GroupName'])
            tradehd.CreateExHandler(item['Exchange'],item['Content'])
            self.__apis.add(tradehd)
        pass
 
    #开启监视器
    def create_order(self,side,symbol, price=0):
        for tradehd in self.__apis:
            if side==BUY:
                #买
                order,err_msg=tradehd.CreateOrder(symbol,MARKET,BUY,self.__qty)
                if order==None:
                    wspush=WebPush()
                    wspush.sendmsg(f'{tradehd.group_name} 开买单失败,{err_msg}')
            else:
                #卖,查出来全卖掉
                coin=''
                symbollist=symbol.split('/')
                if len(symbollist)>1:
                    coin=symbollist[0]
                balance=tradehd.FetchBalance()
                if balance!=None and len(coin)>0:
                    symbol_qty=balance['total'][coin]
                    order,err_msg = tradehd.CreateOrder(symbol,MARKET,SELL,symbol_qty)
                    if order == None:
                        wspush=WebPush()
                        wspush.sendmsg(f'{tradehd.group_name} 卖单失败,{err_msg}')
                pass
        pass

    #关闭网格
    def stop(self):
        pass