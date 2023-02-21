# -*- coding: utf-8 -*-
from common.common import RecordData,Func_DecimalCut2,SELL,LIMIT,greater_or_equal,TP_FLT_PER,TP_FLT_NUM

import traceback

class FloatingTPTask():
    def __init__(self,tradhd,condata,tpdata,qty,price):
        self._tradeobj=tradhd   #交易对象句柄
        self._symbol=condata['Symbol']   #交易品种
        # self._price_res=condata['PriceRes']     
        # #行情精度
        self._pmin=condata['PMin']
        self._pdigit=condata['PDigit']
        self._flt_point=tpdata['TPFLTPoint']    #浮盈值
        self._flt_mode=tpdata['TPFLTMode']      #浮盈模式
        self._his_max_price=0.0        #历史最高价(从创建对象之后)
        self._trader_qty=qty   #经过计算后,扣除交易所税费之后所得的币数
        self._trader_price=price    #下单时候的价格
        self._errnum=0
        self._stop_price=Func_DecimalCut2(price*(1-condata['StopPercent']),self._pdigit,self._pmin)
        pass
    
    def __str__(self):
        return self._tradeobj['TraderName']
    
    def run(self):
        try:
            ticker=self._tradeobj['TradeHD'].FetchTicker(self._symbol)
            if ticker==None or ticker['last'] <= 0.0:
                raise Exception('查询行情错误')
            
            last=ticker['last']
            
            #如果止损价格大于等于最新价,触发止损
            if greater_or_equal(self._stop_price,last):
                order,err_msg=self._tradeobj['TradeHD'].CreateOrder(self._symbol,LIMIT,SELL,self._trader_qty,last)
                if order!=None:
                    msg=''
                    if order!=None:
                        msg='下单成功,品种为{0},数量为{1},价格为{2},委托号为{3}'.format(self._symbol,self._trader_qty,last,order['id'])
                    else:
                        msg=f'下单失败,原因为:{err_msg}'
                        
                    RecordData('{0} 触发止损 {1}'.format(self._tradehd.group_name,msg))
            
            #交易价格大于等于行情价时不会计算浮盈
            if greater_or_equal(self._trader_price,last): 
                return False
            
            #如果最新价比历史最高价大于或等于,记录历史最高价
            if greater_or_equal(last,self._his_max_price,self._price_res): 
                self._his_max_price=last  
                return False
            else:
                #计算出有最高价时的止盈价格
                #公式: 百分比: 卖出价=最高价*(1-配置值)
                #      固定值: 卖出价=最高价-配置值
                flt_min_price=Func_DecimalCut2(
                    self._his_max_price*(1-self._flt_point)\
                        if self._flt_mode == TP_FLT_PER else\
                    (self._his_max_price- self._flt_point),
                    self._pdigit,
                    self._pmin 
                )
                
                #公式: 百分比: 卖出价=(最高价 - 买入价)*(1-配置值)+买入价
                #      固定值: 卖出价=(最高价-买入价)-配置值+买入价
                flt_min_price=Func_DecimalCut2(
                    ((self._his_max_price-self._trader_price)*(1-self._flt_point)+self._trader_price) \
                        if self._flt_mode == TP_FLT_PER else \
                    ((self._his_max_price-self._trader_price)-self._flt_point+self._trader_price),
                    self._pdigit,
                    self._pmin
                )
                
                if greater_or_equal(flt_min_price,last,self._price_res): #止盈价格大于等于最新价,触发止盈
                    order,err_msg=self._tradeobj['TradeHD'].CreateOrder(self._symbol,LIMIT,SELL,self._trader_qty,last)
                    msg=''
                    if order!=None:
                        msg='下单成功'
                    else:
                        msg=f'下单失败,原因为:{err_msg}'
                        
                    RecordData('{0} 触发止盈 {1}'.format(self._tradehd.group_name,msg))
                    return True
                self._errnum=0
                return False
        except:
            msg=traceback.format_exc()
            RecordData(msg)
            self._errnum=self._errnum+1
            if self._errnum >=10: #连续错误10次就直接退出任务
                return True
            return False