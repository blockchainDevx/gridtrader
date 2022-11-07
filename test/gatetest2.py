import ccxt
import  json
import time

def Func_DecimalCut(f,n):
    return float(int(f*10**n)/10**n)


trade=ccxt.gateio({
    'apiKey':key,
    'secret':secret,
    'options': {
        'defaultType': 'spot',
        },
})




balance=trade.fetch_balance()
print(f'\tbalance {json.dumps(balance)}')

tick=trade.fetch_ticker('ETH/USDT')
print(f'\ttick{json.dumps(tick)}')
# qty=Func_DecimalCut(balance['total']['USDT']/tick['last'],4)
# order=trade.create_order('ETH/USDT','limit','buy',qty,tick['last'])
# print(f'\torder {json.dumps(order)}')

# order=trade.create_order('ETH/USDT','limit','sell',balance['total']['ETH'],tick['last'])
# print(f'\torder {json.dumps(order)}')

# time.sleep(5)

balance=trade.fetch_balance()
print(f'\tbalance {json.dumps(balance)}')