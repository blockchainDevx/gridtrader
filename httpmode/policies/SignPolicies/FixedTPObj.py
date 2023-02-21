# -*- coding: utf-8 -*-
from pdb import pm
from common.common import LIMIT,SELL,RecordData,greater_or_equal,Func_DecimalCut2
import traceback



class FixedTPTask():
    def __init__(self,tradehd,condata,tpdata,trade_qty,trade_price):
        self._tradehd=tradehd
        self._symbol=condata['Symbol']
        self._tpdata=tpdata
        pmin=condata['PMin']
        pdigit=condata['PDigit']
        self._trade_qty=trade_qty
        self._trade_price=trade_price
        self._stop_price= Func_DecimalCut2((1-condata['StopPercent'])*self._trade_price,pdigit,pmin)
        self._errnum=0
        
    def __str__(self):
        return self._tradehd['TraderName']
        
    def run(self):
        try:
            ticker=self._tradehd['TradeHD'].FetchTicker(self._symbol)
            if ticker==None or ticker['last'] <= 0.0:
                raise Exception('查询行情错误')
            
            last=ticker['last']
            
            #止损,当前价小于等于止损价
            if greater_or_equal(self._stop_price,last):
                order,err_msg=self._tradehd.CreateOrder(self._symbol,LIMIT,SELL,self._trade_qty,last)
                if order!=None:
                    msg=''
                    if order!=None:
                        msg='下单成功,品种为{0},数量为{1},价格为{2},委托号为{3}'.format(self._symbol,self._trader_qty,last,order['id'])
                    else:
                        msg=f'下单失败,原因为:{err_msg}'
                        
                    RecordData('{0} 触发止损 {1}'.format(self._tradehd.group_name,msg))
                    return True
            elif greater_or_equal(last,self._trade_price):  #当前价大于交易价
                
                #筛选出价格小于等于最新价的止盈点
                lis=list(filter(lambda x:greater_or_equal(last,x[1],ret=4),self._tpdata))
                if len(lis) == 0:
                    return False
                elif len(lis) >0:
                    #遍历筛选出来的止盈点,下卖单,将止盈点从列表中删除
                    for item in lis:
                        
                        order,err_msg=self._tradehd.CreateOrder(self._symbol,LIMIT,SELL,item[0],last)
                        if order!=None:
                            msg='下单成功,品种为{0},数量为{1},价格为{2},委托号为{3}'.format(self._symbol,item[0],last,order['id'])
                        else:
                            msg=f'下单失败,原因为:{err_msg}'
                        RecordData('{0} 触发止盈 {1}'.format(self._tradehd.group_name,msg))
                        
                        self._tpdata.remove(item)
                    if len(self._tpdata) ==0:
                        return True
        except:
            msg=traceback.format_exc()
            RecordData(f'{self._tradehd.group_name} 调用失败,原因为: {msg}')
            self._errnum=self._errnum+1
            if self._errnum>=10:
                return True
