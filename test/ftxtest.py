import ccxt
import json


trade=ccxt.ftx({
    'apiKey':key,
    'secret':secret,
    'headers': {
                        'FTX-SUBACCOUNT': subaccount,
                    },
})

balance=trade.fetch_balance()
print(f'\tbalance {json.dumps(balance)}')