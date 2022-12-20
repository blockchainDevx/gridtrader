from common.common import BUY,SELL,LIMIT,RecordData,Func_DecimalCut
from MasterCoin import TradePairHandle
import traceback
def trade_by_ammount_gate(side,item,data):
    ammount_type=data['AmmountType']
    symbol=data['Symbol']
    qty_res=data['QtyRes']
    stop_percent=data['StopPercent']
    price_res=data['PriceRes']

    tradehd=item.get('TraderHD')
    if tradehd==None:
        return None,None
    balance=tradehd.FetchBalance()
    if balance ==None:
        return None,None
    try:
        if side==BUY:#买
            #查看资金,如果账号有U,就买入
            amount= balance['total'][ammount_type]
            if amount<=0:
                RecordData(f'账号 {tradehd.group_name} 买入失败,原因是: 账号没资金')
                return None,None
            
            #查看最新价,计算出合适的买入币量
            tick=tradehd.FetchTicker(symbol)
            if tick==None:
                RecordData(f'账号 {tradehd.group_name} 查询{symbol}最新价失败')
                return None,None
            last=tick['last']
            qty= Func_DecimalCut(amount/last,qty_res)
            
            #配置了止损比例,根据当前价计算出止损价
            stop_price=0.0
            if stop_percent >0 and stop_percent < 1:
                stop_price=Func_DecimalCut(last*(1-stop_percent),price_res)
            
            #下单
            order,err_msg=tradehd.CreateOrder(symbol,LIMIT,BUY,qty,last) if stop_price == 0 else \
                tradehd.CreateOrder(symbol,LIMIT,BUY,qty,last,{
                    'stopPrice':stop_price
                })
                
            #记录下单返回数据
            msg=''
            if order==None:
                msg='失败,原因为:{0}'.format(err_msg)
            else:
                msg='成功'
            RecordData('账号 {0} 买入 {1},买入数量为 {2},当前的价格为 {3},当前账号的资金为 {4}'.
                                format(tradehd.group_name,msg,qty,tick['last'],amount))    
            return qty,tick['last'] if order!=None else None,None                                       
        else: #卖
            #获取币种名称
            coin=''
            symbollist=TradePairHandle(symbol)
            if len(symbollist)==2:
                coin=symbollist[0]
            if len(coin)==0:
                return None,None
            
            #获取账号币数量        
            qty=float(balance['total'][coin])
            
            #获取币种最新价
            tick=tradehd.FetchTicker(symbol)
            if tick==None:
                RecordData(f'账号 {tradehd.group_name} 查询{symbol}最新价失败')
                return
            last=tick['last']
            
            #下单
            order,err_msg = tradehd.CreateOrder(symbol,LIMIT,SELL,qty,last)
            
            #记录下单返回数据
            msg=''
            if order==None:
                msg='失败,原因为:{0}'.format(err_msg)
            else:
                msg='成功'
            RecordData('账号 {0} 卖出 {1},全卖,卖出数量为 {2},卖出价格为 {3}'.
                                format(tradehd.group_name,msg,qty,last))
            return qty,last if order!=None else None,None
    except:
        msg=traceback.format_exc()
        RecordData(f'{tradehd.group_name} 调用失败,原因为: {msg}')
        return None,None
    pass