from common.common import BUY,SELL,LIMIT,MARKET,RecordData,Func_DecimalCut
from .MasterCoin import TradePairHandle
import traceback

def trade_by_ammount_ok(side,item,data):
    amounttype=data['AmmountType']
    symbol=data['Symbol']
    qty_res=data['QtyRes']
    stop_percent=data['StopPercent']
    price_res=data['PriceRes']
    lastside=data['LastSide']
    
    tradehd=item.get('TraderHD')
    if tradehd==None:
        RecordData(f'交易账号未找到')
        return None,None
    balance=tradehd.FetchBalance()
    if balance ==None:
        RecordData(f'交易账号未能查到资金数据')
        return None,None
    try:
        if side==BUY:#信号为买入
            #查账号资金,如果有U,就买入,没U就不买
            amount= balance['total'][amounttype]
            if amount<=0:
                RecordData(f'账号 {tradehd.group_name} 买入失败,原因是: 账号没资金')
                return None,None
            
            #根据最新行情计算出合适的买入币量
            tick=tradehd.FetchTicker(symbol)
            if tick==None:
                RecordData(f'账号 {tradehd.group_name} 查询 {symbol} 最新价失败')
                return None,None
            qty= Func_DecimalCut(amount/tick['last'],qty_res)
            
            #配置了止损比例,根据当前价计算出止损价
            stop_price=0.0
            if stop_percent >0 and stop_percent < 1:
                stop_price=Func_DecimalCut(tick['last']*(1-stop_percent),price_res)
            
            #下单
            order,err_msg=tradehd.CreateOrder(symbol,LIMIT,BUY,qty,tick['last']) if stop_price == 0 else \
                tradehd.CreateOrder(symbol,LIMIT,BUY,qty,tick['last'],params={
                    'sz':qty,
                    'slTriggerPx':stop_price,
                    'slOrdPx':-1
                })
              
            #记录下单返回数据
            msg=''
            if order==None:
                msg='失败,原因为: {0} '.format(err_msg)
            else:
                msg='成功,委托号为 {0} '.format(order['id'])
            RecordData('账号 {0} 买入 {1} ,买入数量为 {2} ,当前的价格为 {3} ,当前账号的资金为 {4} ,设置的止损价格为 {5}'.
                                format(tradehd.group_name,msg,qty,tick['last'],amount,stop_price))
            return qty,tick['last'] if order!=None else None,None                                           
        elif side == SELL: #信号为卖
            #查账号资金,有币就卖,没有就不卖
            coin=''
            symbollist=TradePairHandle(symbol)
            if len(symbollist)==2:
                coin=symbollist[0]
            
            if len(coin) == 0:
                RecordData(f'交易币种信息错误')
                return None,None
            
            #查看币量
            qty=float(balance['total'][coin])
            
            #下单
            order,err_msg = tradehd.CreateOrder(symbol,MARKET,SELL,qty)
            
            #记录下单返回数据
            msg=''
            if order==None:
                msg='失败,原因为:{0}'.format(err_msg)
            else:
                msg='成功,委托号为{0}'.format(order['id'])
            tick=tradehd.FetchTicker(symbol)
            RecordData('账号 {0} 卖出 {1} ,全卖,卖出数量为 {2} ,当前价格为 {3} ,委托号为 {4}'.
                                format(tradehd.group_name,msg,qty,tick['last']))
            return qty,tick['last'] if order!=None else None,None
    except:
        msg=traceback.format_exc()
        RecordData(f'{tradehd.group_name} 调用失败,原因为: {msg}')
        return None,None