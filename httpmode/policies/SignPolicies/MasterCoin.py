
__all__=['IsMasterCoin','TradePairHandle']
Master=[
    'BTC',
    'ETH',
]

def IsMasterCoin(symbol):
    strlist=TradePairHandle(symbol)
    if strlist!=None:
        if strlist[0] in Master:
            return True
    return False

def TradePairHandle(symbol):
    if '/' in symbol:
        return symbol.split('/')
    elif '_' in symbol:
        return symbol.split('_')
    else:
        return None