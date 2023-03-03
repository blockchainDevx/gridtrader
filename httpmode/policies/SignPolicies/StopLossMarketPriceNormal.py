import traceback
from .MasterCoin import TradePairHandle
from common.common import LOG_STORE, Func_DecimalCut2,RecordData,MARKET,SELL,BUY,LOG_STORE
import sys

def stoploss(tradeHD,symbol,qdigit,qmin):
    try:
        #1.撤销账号里的买委托
        id=tradeHD.order_ids.get(f'{symbol}')
        if id!=None:
            order=tradeHD.FetchOrder(id,symbol)
            if order!=None:
                if order['side'] == BUY and order['status'] != 'closed': #买单,不是完成状态
                    tradeHD.CancelOrder(id,symbol)
                    RecordData(f'{tradeHD.group_name} 取消委托,委托号为: {id}')
        
        #2.账号里持有的币清空
        symbollist=TradePairHandle(symbol)
        coin=symbollist[0]
        balance=tradeHD.FetchBalance()
        qty=Func_DecimalCut2(balance['total'][coin],qdigit,qmin)
        if qty<=sys.float_info.epsilon:
            return
        order,err_msg=tradeHD.CreateOrder(symbol,MARKET,SELL,qty)
        msg=''
        if order!=None:
            msg='下单成功,委托号为{0}'.format(order['id'])
        else:
            msg=f'下单失败,原因为:{err_msg}'
            
        RecordData('{0} 市价平仓,品种为 {1} ,数量为 {2} : {3}'.format(tradeHD.group_name,
                symbol,
                qty,
                msg))
    except:
        msg=traceback.format_exc()
        RecordData(msg)