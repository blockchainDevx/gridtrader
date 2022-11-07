import ccxt
import json
import sys
from httpmode.trdapiwrap.TraderAPI import TraderAPI


def log(msg,withTime=True):
        try:
            f=open(f"markets.log",'a')
            f.write(msg+"\n")
            f.close()
        except:
            pass
        
BUY='buy'
SELL='sell'
LIMIT='limit'

def Func_DecimalCut(f,n):
    return float(int(f*10**n)/10**n)

class Test():
    def __init__(self,amounttype,symbol,qty_res):
        self.__amounttype=amounttype
        self.__symbol=symbol
        self.__qty_res=qty_res
        
    def trade_by_ammount_gate(self,side,item):
            tradehd=item.get('traderhd')
            if tradehd==None:
                print('tradehd not found')
                return
            balance=tradehd.FetchBalance()
            if balance ==None:
                print('balance not found')
                return
            try:
                if side==BUY:#买
                    amount= balance['total'][self.__amounttype]
                    if amount<=0:
                        print(f'账号 {tradehd.group_name} 买入失败,原因是: 账号没资金')
                        # SignPolicy.Record(f'账号 {tradehd.group_name} 买入失败,原因是: 账号没资金')
                        return
                    tick=tradehd.FetchTicker(self.__symbol)
                    if tick==None:
                        # SignPolicy.Record(f'账号 {tradehd.group_name} 查询{self.__symbol}最新价失败')
                        print(f'账号 {tradehd.group_name} 查询{self.__symbol}最新价失败')
                        return
                    last=tick['last']
                    qty= Func_DecimalCut(amount/last,self.__qty_res)
                    order,err_msg=tradehd.CreateOrder(self.__symbol,LIMIT,BUY,qty,last)
                    msg=''
                    if order==None:
                        print(err_msg)
                        msg='失败,原因为:{0}'.format(err_msg)
                    else:
                        msg='成功'
                    # SignPolicy.Record('账号 {0} 买入 {1},买入数量为 {2},当前的价格为 {3},当前账号的资金为 {4}'.
                    #                   format(tradehd.group_name,msg,qty,tick['last'],amount))    
                    print('账号 {0} 买入 {1},买入数量为 {2},当前的价格为 {3},当前账号的资金为 {4}'.
                                    format(tradehd.group_name,msg,qty,last,amount))                                       
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
                            print(f'账号 {tradehd.group_name} 查询{self.__symbol}最新价失败')
                            # SignPolicy.Record(f'账号 {tradehd.group_name} 查询{self.__symbol}最新价失败')
                            return
                        last=tick['last']
                        order,err_msg = tradehd.CreateOrder(self.__symbol,LIMIT,SELL,symbol_qty,last)
                        msg=''
                        if order==None:
                            msg='失败,原因为:{0}'.format(err_msg)
                        else:
                            msg='成功'
                        # SignPolicy.Record('账号 {0} 卖出 {1},全卖,卖出数量为 {2},卖出价格为 {3}'.
                        #                   format(tradehd.group_name,msg,symbol_qty,last))
                        print('账号 {0} 卖出 {1},全卖,卖出数量为 {2},卖出价格为 {3}'.
                                        format(tradehd.group_name,msg,symbol_qty,last))
            except Exception as e:
                # SignPolicy.Record(f'{tradehd.group_name} 调用失败,原因为: {str(e)}')
                print(f'{tradehd.group_name} 调用失败,原因为: {str(e)}')
            pass        

# key='cc2530771c1e788d4c38027ce9543a2e'
# secret='696ce9ec9e4834a40f95d9cf05f312bb54388184d3306e7b8165ade575a1f38c'
key='12b8206f6ecf5c947107a63ec5802234'
secret='02f01d0c1ddab499140fe7eb1606a285d2bf0df357a139661355763611a6ead'

tradhd=TraderAPI('test')
tradhd.CreateExHandler('gate',{"API":{
    'ApiKey':key,
    'Secret':secret
}})

item={
    'traderhd':tradhd,
    'exchange':'gate'
}
order=tradhd.FetchBalance()
print(f'order: {json.dumps(order)}')
# testobj=Test('USDT','ETH/USDT',4)
# testobj.trade_by_ammount_gate(BUY,item)
# print('=======================================')
# testobj.trade_by_ammount_gate(SELL,item)


# ex=ccxt.gateio({
#     'apiKey': 'cc2530771c1e788d4c38027ce9543a2e',
#     'secret': '696ce9ec9e4834a40f95d9cf05f312bb54388184d3306e7b8165ade575a1f38c',
#     'options': {
#         'defaultType': 'future',
#     },
# })

# balance=ex.fetch_balance()
# print('balance:{0}'.format(json.dumps(balance)))

# # usdt=float(balance['total']['USDT'])

# symbol='ETH_USDT'
# order=ex.create_order(symbol,'market','buy',0.01)
# print('\torder:{0}'.format(json.dumps(order)))

# markets=ex.load_markets()
# # print('markets:{0}'.format(json.dumps(markets)))
# log(json.dumps(markets))

# order=ex.create_order(symbol,'market','buy',)

# ticker=ex.fetch_ticker(symbol)
# last=ticker['last']

# order=ex.create_order(symbol,'limit','buy',usdt/last,last)
# print('\torder:{0}'.format(json.dumps(order)))

# order=ex.fetch_order(id=order['id'],symbol=symbol)
# print('\torder:{0}'.format(json.dumps(order)))

# balance=ex.fetch_balance()
# print('\tbalance:{0}'.format(json.dumps(balance)))
# eth=float(balance['total']['ETH'])

# ticker=ex.fetch_ticker(symbol)
# last=ticker['last']
# order=ex.create_order(symbol,'limit','sell',eth,last)
# print('\torder:{0}'.format(json.dumps(order)))


# order=ex.fetch_order(id=order['id'],symbol=symbol)
# print('\torder:{0}'.format(json.dumps(order)))

# balance=ex.fetch_balance()
# print('\tbalance:{0}'.format(json.dumps(balance)))


# order=ex.create_order(symbol,'limit','sell',eth,last,{
#     'account':'spot'
# })
# print('\torder:{0}'.format(json.dumps(order)))

# balance=ex.fetch_balance()
# print('\tbalance:{0}'.format(json.dumps(balance)))

# order=ex.fetch_order(id=order['id'],symbol=symbol)
# print('\torder:{0}'.format(json.dumps(order)))

# order=ex.cancel_order(id='214991603641',symbol=symbol)
# print('\torder:{0}'.format(json.dumps(order)))