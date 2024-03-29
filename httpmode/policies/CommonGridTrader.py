import threading
import ccxt
import sys

from common.common import LOG_STORE, Func_DecimalCut2,Record

#
class IGridTrader():
    def __init__(self):
        self.has_qty=0
        self.buy_num=0
        self.sell_num=0
        self.lock=threading.Lock()
        self.thread={}
        self.coin=''        
        pass
    
    #参数检查
    @staticmethod
    def parms_check(json_data):
        pass

    #网格计算
    @staticmethod
    def grid_calc(api,data):
        pass

    #读取配置
    def read_config_by_obj(self,api,json_data):
        pass

    #网格开始
    def start(self,factor=0):
        pass

    #开启监视器
    def create_monitor(self,orderid,lock):
        pass

    #关闭网格
    def stop(self):
        pass

#创建网格
def Func_CreateGrid(data):
    ratio= data.get('Ratio')
    taker=data.get('Taker')
    fund=data.get('Fund')
    qty=data.get('Qty')
    lower=data.get('Lower')
    pmin=data.get('PMin')
    pdigit=data.get('PDigit')
    qmin=data.get('QMin')
    qdigit=data.get('QDigit')

    if ratio==None \
        or taker==None \
        or fund==None \
        or qty==None \
        or lower==None \
        or pmin==None \
        or pdigit==None \
        or qmin==None \
        or qdigit==None:
        return None
    
    grid_list=[]
    for i in range(0,qty):
        #此格的下沿价格
        low_price=lower*(1+ratio)**(i)
        low_price=Func_DecimalCut2(low_price,pdigit,pmin)
        #此格的上沿价格
        up_price=low_price*(1+ratio)
        up_price=Func_DecimalCut2(up_price,pdigit,pmin)
        #此格买入的手数
        buy_qty=fund/low_price
        buy_qty=Func_DecimalCut2(buy_qty,qdigit,qmin)
        
        #此格卖出的手数
        sell_qty=fund/low_price*(1-taker)
        sell_qty=Func_DecimalCut2(sell_qty,qdigit,qmin)
        if buy_qty < sys.float_info.epsilon or sell_qty < sys.float_info.epsilon:
            return False,None

        grid_list.append(dict([
            ('LowPrice',low_price),
            ('UpPrice',up_price),
            ('BuyQty',buy_qty),
            ('SellQty',sell_qty),
            ('Id',''),
            ('Side','')
            ]))
        Record(f'网格编号{i+1} 下沿价格:{low_price},上沿价格:{up_price},买入手数:{buy_qty},卖出手数:{sell_qty}',level=LOG_STORE)
    return grid_list
    pass






            