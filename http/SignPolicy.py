from CommonGridTrader import *
from TraderAPI import TraderAPI
from common import *
from WebPush import WebPush
from Logger import Logger

class SignPolicy(IGridTrader):
    ALL=99
    def __init__(self,qty,symbol,signtype,key,qty_min):
        self.__symbol=symbol
        self.__qty=int(qty)
        self.__keyname=key
        self.__qty_res=qty_min
        self.__apis=[]
        self.__signtype=signtype


    #网格开始
    def start(self,apilist):
        for item in apilist:
            groupname=item['GroupName']
            tradehd=TraderAPI(groupname)
            tradehd.CreateExHandler(item['Exchange'],item['Content'])
            _,taker=tradehd.FetchTradingFee(self.__symbol)
            self.__apis.append({ 
                'traderhd':tradehd,
                'taker':taker})
            
            SignPolicy.Record(f'=====网页 {self.__keyname} 启动,账号:{groupname},'\
                f'品种为:{self.__symbol},信号类别为:{self.__signtype}======')
        pass
 
    #开启监视器
    def create_order(self,side, price=0):
        SignPolicy.Record(f'---------网页 {self.__keyname} 触发信号---------')
        SignPolicy.Record(f'信号触发:方向为:{side},品种:{self.__symbol},信号类别为:{self.__signtype}')
        for item in self.__apis:
            self.trade_by_account(side,item)
            pass
        pass
        SignPolicy.Record(f'------------------------------------')


    def trade_by_qty(self,side,item):
        tradehd=item.get('traderhd')
        taker=item.get('taker')
        if tradehd==None or taker==None:
            return
        try:
            if side==BUY:
                        #买
                order,err_msg=tradehd.CreateOrder(self.__symbol,MARKET,BUY,self.__qty)
                if order==None:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 买入失败,原因为: {err_msg}')
                else:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 买入成功,买入币数: {self.__qty}')
            else:
                #卖,查出来全卖掉
                sell_qty=Func_DecimalCut(self.__qty*(1-taker),self.__qty_res)
                order,err_msg=tradehd.CreateOrder(self.__symbol,MARKET,SELL,sell_qty)
                if order==None:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 卖出失败,原因为: {err_msg}')
                else:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 卖出成功,卖出币数: {sell_qty}')
        except Exception as e:
            SignPolicy.Record(f'{tradehd.group_name} 调用失败,原因为: {str(e)}')
            
    
    def trade_by_account(self,side,item):
        tradehd=item.get('traderhd')
        if tradehd==None:
            return
        try:
            if side==BUY:#买
                order,err_msg=tradehd.CreateOrder(self.__symbol,MARKET,BUY,SignPolicy.ALL)
                if order==None:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 买入失败,原因为: {err_msg}')
                else:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 买入成功,全买')
            else:
                coin=''
                symbollist=self.__symbol.split('/')
                if len(symbollist)>1:
                    coin=symbollist[0]
                balance=tradehd.FetchBalance()
                if balance!=None and len(coin)>0:
                    symbol_qty=balance['total'][coin]
                    order,err_msg = tradehd.CreateOrder(self.__symbol,MARKET,SELL,symbol_qty)
                    if order==None:
                        SignPolicy.Record(f'账号 {tradehd.group_name} 卖出失败,原因为: {err_msg}')
                    else:
                        SignPolicy.Record(f'账号 {tradehd.group_name} 卖出成功,全卖')
        except Exception as e:
            SignPolicy.Record(f'{tradehd.group_name} 调用失败,原因为: {str(e)}')
            
    #关闭网格
    def stop(self):
        pass
    
    @staticmethod
    def Record(msg):
        print(msg)
        Logger().log(msg)
        WebPush().sendmsg(msg)