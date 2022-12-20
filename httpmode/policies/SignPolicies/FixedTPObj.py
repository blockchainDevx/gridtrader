# -*- coding: utf-8 -*-
from common.common import LIMIT,SELL,RecordData,greater_or_equal
import traceback



class FixedTPTask():
    def __init__(self,tradehd,condata,tpdata):
        self._tradehd=tradehd
        self._symbol=condata['Symbol']
        self._tpdata=tpdata
        self._errnum=0
        
    def __str__(self):
        return self._tradehd['TraderName']
        
    def run(self):
        try:
            ticker=self._tradehd['TradeHD'].FetchTicker(self._symbol)
            if ticker==None or ticker['last'] <= 0.0:
                raise Exception('查询行情错误')
            
            #筛选出价格小于等于最新价的止盈点
            lis=list(filter(lambda x:greater_or_equal(ticker['last'],x[1],ret=4),self._tpdata))
            if len(lis) == 0:
                return False
            elif len(lis) >0:
                #遍历筛选出来的止盈点,下卖单,将止盈点从列表中删除
                for item in lis:
                    self._tradehd.CreateOrder(self._symbol,LIMIT,SELL,item[0],item[1])
                    self._tpdata.remove(item)
                if len(self._tpdata) ==0:
                    return True
        except:
            msg=traceback.format_exc()
            RecordData(f'{self._tradehd.group_name} 调用失败,原因为: {msg}')
            self._errnum=self._errnum+1
            if self._errnum>=10:
                return True
