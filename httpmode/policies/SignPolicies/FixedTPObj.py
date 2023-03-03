# -*- coding: utf-8 -*-
from common.common import LIMIT,SELL,Record,RecordData, greater_or_equal,Func_DecimalCut2,LOG_STORE
from .StopLossMarketPriceNormal import stoploss
import traceback

class FixedTPTask():
    def __init__(self,tradehd,condata,tpdata,trade_qty,trade_price):
        self._tradehd=tradehd
        self._symbol=condata['Symbol']
        self._tpdata=tpdata
        self._qmin=condata['QMin']
        self._qdigit=condata['QDigit']
        pmin=condata['PMin']
        pdigit=condata['PDigit']
        self._trade_price=trade_price
        self._stop_price= Func_DecimalCut2((1-condata['StopPercent'])*self._trade_price,pdigit,pmin)
        self._errnum=0
        
    def __str__(self):
        return self._tradehd['TraderName']
        
    def run(self):
        try:
            ticker=self._tradehd['TraderHD'].FetchTicker(self._symbol)
            if ticker==None or ticker['last'] <= 0.0:
                raise Exception('查询行情错误')
            
            last=ticker['last']
            
            #止损,当前价小于等于止损价
            if greater_or_equal(self._stop_price,last):
                RecordData('{0}  触发止损,品种为 {1} 当前价格为 {2},设置的止损价格为 {3}'.format(self._tradehd['TraderHD'].group_name,
                    self._symbol,last,self._stop_price))
                stoploss(self._tradehd['TraderHD'], self._symbol, self._qdigit, self._qmin)
                return True,self._tradehd['TraderName']
            elif greater_or_equal(last,self._trade_price):  #当前价大于交易价
                
                #筛选出价格小于等于最新价的止盈点
                lis=list(filter(lambda x:greater_or_equal(last,x[1]),self._tpdata))
                if len(lis) == 0:
                    return False,''
                elif len(lis) >0:
                    #遍历筛选出来的止盈点,下卖单,将止盈点从列表中删除
                    for item in lis: 
                        
                        order,err_msg=self._tradehd['TraderHD'].CreateOrder(self._symbol,LIMIT,SELL,item[0],last)
                        if order!=None:
                            msg='下单成功,品种为{0},数量为{1},价格为{2},委托号为{3}'.format(self._symbol,item[0],last,order['id'])
                        else:
                            msg=f'下单失败,原因为:{err_msg}'
                        RecordData('{0} 触发止盈 {1}'.format(self._tradehd['TraderHD'].group_name,msg))
                        
                        self._tpdata.remove(item)
                    if len(self._tpdata) ==0:
                        return True,self._tradehd['TraderName']
            else:
                return False,''
        except:
            msg=traceback.format_exc()
            Record('调用失败 次数 {0},原因为: {1}'.format( self._errnum,msg),level=LOG_STORE)
            self._errnum=self._errnum+1
            if self._errnum>=10:
                return True,self._tradehd['TraderName']
            return False,''
