from policies.CommonGridTrader import *
from trdapiwrap.TraderAPI import TraderAPI
from common.common import *
from WebPush import WebPush
from common.logger.Logger import Logger

class SignPolicy(IGridTrader):
    def __init__(self,qty,symbol,signtype,key,qty_min):
        self.__symbol=symbol
        self.__qty=int(qty)
        self.__keyname=key
        self.__qty_res=qty_min
        self.__apis=[]
        self.__signtype=signtype
        symbollist=self.__symbol.split('/')
        if len(symbollist)==2:
            self.__cointype=symbollist[0]
            self.__amounttype=symbollist[1]
        else:
            self.__cointype=''
            self.__amounttype=''


    #网格开始
    def start(self,apilist):
        for item in apilist:
            groupname=item['GroupName']
            tradehd=TraderAPI(groupname)
            tradehd.CreateExHandler(item['Exchange'],item['Content'])
            _,taker=tradehd.FetchTradingFee(self.__symbol)
            self.__apis.append({ 
                'traderhd':tradehd,
                'exchange':item['Exchange'],
                'taker':taker})
            
            SignPolicy.Record(f'=====网页 {self.__keyname} 启动,账号:{groupname},'\
                f'品种为:{self.__symbol},信号类别为:{self.__signtype}======')
        pass
 
    #开启监视器
    def create_order(self,side, price=0):
        SignPolicy.Record(f'---------网页 {self.__keyname} 触发信号---------')
        SignPolicy.Record(f'信号触发:方向为:{side},品种:{self.__symbol},信号类别为:{self.__signtype}')
        for item in self.__apis:
            if item['exchange']== GATE:
                self.trade_by_ammount_gate(side,item)
            else:
                self.trade_by_ammount_normal(side,item)
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
    
    def trade_by_ammount_normal(self,side,item):
        tradehd=item.get('traderhd')
        if tradehd==None:
            return
        balance=tradehd.FetchBalance()
        if balance ==None:
            return
        try:
            if side==BUY:#买
                amount= balance['total'][self.__amounttype]
                if amount<=0:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 买入失败,原因是: 账号没资金')
                    return
                tick=tradehd.FetchTicker(self.__symbol)
                if tick==None:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 查询{self.__symbol}最新价失败')
                    return
                qty= Func_DecimalCut(amount/tick['last'],self.__qty_res)
                order,err_msg=tradehd.CreateOrder(self.__symbol,MARKET,BUY,qty)
                msg=''
                if order==None:
                    msg='失败,原因为:{0}'.format(err_msg)
                else:
                    msg='成功'
                SignPolicy.Record('账号 {0} 买入 {1},买入数量为 {2},当前的价格为 {3},当前账号的资金为 {4}'.
                                  format(tradehd.group_name,msg,qty,tick['last'],amount))                                           
            else:
                coin=''
                symbollist=self.__symbol.split('/')
                if len(symbollist)>1:
                    coin=symbollist[0]
                balance=tradehd.FetchBalance()
                if balance!=None and len(coin)>0:
                    symbol_qty=float(balance['total'][coin])
                    order,err_msg = tradehd.CreateOrder(self.__symbol,MARKET,SELL,symbol_qty)
                    msg=''
                    if order==None:
                        msg='失败,原因为:{0}'.format(err_msg)
                    else:
                        msg='成功'
                    tick=tradehd.FetchTicker(self.__symbol)
                    SignPolicy.Record('账号 {0} 卖出 {1},全卖,卖出数量为 {2},当前价格为 {3}'.
                                      format(tradehd.group_name,msg,symbol_qty,tick['last']))
        except Exception as e:
            SignPolicy.Record(f'{tradehd.group_name} 调用失败,原因为: {str(e)}')
            
    '''
    gate现货只支持限价单
    '''
    def trade_by_ammount_gate(self,side,item):
        tradehd=item.get('traderhd')
        if tradehd==None:
            return
        balance=tradehd.FetchBalance()
        if balance ==None:
            return
        try:
            if side==BUY:#买
                amount= balance['total'][self.__amounttype]
                if amount<=0:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 买入失败,原因是: 账号没资金')
                    return
                tick=tradehd.FetchTicker(self.__symbol)
                if tick==None:
                    SignPolicy.Record(f'账号 {tradehd.group_name} 查询{self.__symbol}最新价失败')
                    return
                last=tick['last']
                qty= Func_DecimalCut(amount/last,self.__qty_res)
                order,err_msg=tradehd.CreateOrder(self.__symbol,LIMIT,BUY,qty,last)
                msg=''
                if order==None:
                    msg='失败,原因为:{0}'.format(err_msg)
                else:
                    msg='成功'
                SignPolicy.Record('账号 {0} 买入 {1},买入数量为 {2},当前的价格为 {3},当前账号的资金为 {4}'.
                                  format(tradehd.group_name,msg,qty,tick['last'],amount))                                           
            else:
                coin=''
                symbollist=self.__symbol.split('/')
                if len(symbollist)==2:
                    coin=symbollist[0]
                else:
                    return
                balance=tradehd.FetchBalance()
                if balance!=None and len(coin)>0:
                    symbol_qty=float(balance['total'][coin])
                    tick=tradehd.FetchTicker(self.__symbol)
                    if tick==None:
                        SignPolicy.Record(f'账号 {tradehd.group_name} 查询{self.__symbol}最新价失败')
                        return
                    last=tick['last']
                    order,err_msg = tradehd.CreateOrder(self.__symbol,LIMIT,SELL,symbol_qty,last)
                    msg=''
                    if order==None:
                        msg='失败,原因为:{0}'.format(err_msg)
                    else:
                        msg='成功'
                    SignPolicy.Record('账号 {0} 卖出 {1},全卖,卖出数量为 {2},卖出价格为 {3}'.
                                      format(tradehd.group_name,msg,symbol_qty,last))
        except Exception as e:
            SignPolicy.Record(f'{tradehd.group_name} 调用失败,原因为: {str(e)}')
        pass
    
            
    #关闭网格
    def stop(self):
        pass
    
    @staticmethod
    def Record(msg):
        print(msg)
        Logger().log(msg)
        WebPush().sendmsg(msg)