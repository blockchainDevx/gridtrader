from common.common import BUY,SELL,MARKET,RecordData,Func_DecimalCut
import traceback

def trade_by_qty(side,item,data):
    symbol=data['Symbol']
    qty=data['Qty']
    qty_res=data['QtyRes']
    
    tradehd=item.get('TraderHD')
    taker=item.get('Taker')
    if tradehd==None or taker==None:
        return
    
    try:
        if side==BUY:#买
            balance=tradehd.FetchBalance()                
            order,err_msg=tradehd.CreateOrder(symbol,MARKET,BUY,qty)
            msg=''
            if order==None:
                msg='失败,原因为:{0}'.format(err_msg)
            else:
                msg='成功,委托号为{0}'.format(order['id'])
            RecordData('账号 {0} 买入 {1},买入数量为 {2},当前账号的资金为 {3},委托号为 {4}'.\
                            format(tradehd.group_name,msg,qty,balance))
        else:
            #卖,查出来全卖掉
            sell_qty=Func_DecimalCut(qty*(1-taker),qty_res)
            order,err_msg=tradehd.CreateOrder(symbol,MARKET,SELL,sell_qty)
            msg=''
            if order==None:
                msg='失败,原因为:{0}'.format(err_msg)
            else:
                msg='成功,委托号为{0}'.format(order['id'])
            RecordData(f'账号 {tradehd.group_name} 卖出{msg},卖出币数: {sell_qty}')
    except:
        msg=traceback.format_exc()
        RecordData(f'{tradehd.group_name} 调用失败,原因为: {msg}')
    pass