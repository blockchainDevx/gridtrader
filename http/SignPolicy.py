from CommonGridTrader import *
from TraderAPI import TraderAPI
from common import *
from WebPush import WebPush
from Logger import Logger

class SignPolicy(IGridTrader):
    __apis=set()
    __qty=0.0
    __symbol=''
    __keyname=''

    def __init__(self,qty,symbol,key):
        self.__symbol=symbol
        self.__qty=int(qty)
        self.__keyname=key


    #网格开始
    def start(self,apilist):
        for item in apilist:
            tradehd=TraderAPI(item['GroupName'])
            tradehd.CreateExHandler(item['Exchange'],item['Content'])
            self.__apis.add(tradehd)
        pass
 
    #开启监视器
    def create_order(self,side, price=0):
        print(f'触发信号,{side},{self.__symbol}')
        Logger().log(f'网页 {self.__keyname} 触发信号,方向为:{side},品种:{self.__symbol}')
        for tradehd in self.__apis:
            try:
                if side==BUY:
                    #买
                    print(f'触发信号,买,{self.__symbol}')
                    order,err_msg=tradehd.CreateOrder(self.__symbol,MARKET,BUY,self.__qty)
                    if order==None:
                        wspush=WebPush()
                        wspush.sendmsg(f'{tradehd.group_name} 开买单失败,{err_msg}')
                    else:
                        wspush=WebPush()
                        wspush.sendmsg(f'{tradehd.group_name} 开买单成功')
                    print('买完成')
                else:
                    #卖,查出来全卖掉
                    print(f'触发信号,卖,{self.__symbol}')
                    coin=''
                    symbollist=self.__symbol.split('/')
                    if len(symbollist)>1:
                        coin=symbollist[0]
                    balance=tradehd.FetchBalance()
                    if balance!=None and len(coin)>0:
                        symbol_qty=balance['total'][coin]
                        order,err_msg = tradehd.CreateOrder(self.__symbol,MARKET,SELL,symbol_qty)
                        if order == None:
                            wspush=WebPush()
                            wspush.sendmsg(f'{tradehd.group_name} 卖单失败,{err_msg}')
                        else:
                            wspush=WebPush()
                            wspush.sendmsg(f'{tradehd.group_name} 卖单成功')
                    pass
                    print('卖完成')
            except Exception as e:
                Logger().log(f'网页{self.__keyname}信号触发 {side},{self.__symbol}错误,错误原因为:{str(e)}')
                pass
        pass

    #关闭网格
    def stop(self):
        pass