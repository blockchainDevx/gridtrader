from ast import ExceptHandler
from datetime import datetime
from attr import has
import ccxt 
import time 
import configparser
import pytz
import math
import sys
import atexit
import json

'''
    create_order 市价单,返回的数据结构
    {
        'info': 
            {
                'clOrdId': 'e847386590ce4dBC66c0ed43a0db6c96', 
                'ordId': '424582917040529410', 
                'sCode': '0', 
                'sMsg': '', 
                'tag': ''
            }, 
        'id': '424582917040529410', 
        'clientOrderId': 'e847386590ce4dBC66c0ed43a0db6c96', 
        'timestamp': None, 'datetime': None, 
        'lastTradeTimestamp': None, 
        'symbol': 'ETH/USDT', 
        'type': 'market', 
        'timeInForce': None, 
        'postOnly': None, 
        'side': 'buy', 
        'price': None, 
        'stopPrice': None, 
        'average': None, 
        'cost': None, 
        'amount': None, 
        'filled': None, 
        'remaining': None, 
        'status': None, 
        'fee': None, 
        'trades': [], 
        'fees': []
    }
'''

'''
    create_order 挂单,返回的数据结构
    {
        'info': 
            {
                'clOrdId': 'e847386590ce4dBC9f39db9c328e3101', 
                'ordId': '424562251906048002', 
                'sCode': '0', 
                'sMsg': '', 
                'tag': ''
            }, 
        'id': '424562251906048002', 
        'clientOrderId': 'e847386590ce4dBC9f39db9c328e3101', 
        'timestamp': None, 
        'datetime': None, 
        'lastTradeTimestamp': None, 
        'symbol': 'ETH/USDT', 
        'type': 'limit', 
        'timeInForce': None, 
        'postOnly': None, 
        'side': 'buy', 
        'price': None, 
        'stopPrice': None, 
        'average': None, 
        'cost': None, 
        'amount': None, 
        'filled': None, 
        'remaining': None, 
        'status': None, 
        'fee': None, 
        'trades': [], 
        'fees': []
    }
'''
'''
    fetch_order 市价买成交返回接口数据结构
    {
        'info': 
        {
            'accFillSz': '0.001', 
            'avgPx': '2751.21', 
            'cTime': '1647500599770', 
            'category': 'normal', 
            'ccy': '', 
            'clOrdId': 'e847386590ce4dBC34e5fd928fb0b207', 
            'fee': '-0.000001', 
            'feeCcy': 'ETH', 
            'fillPx': '2751.21', 
            'fillSz': '0.001', 
            'fillTime': '1647500599775', 
            'instId': 'ETH-USDT', 
            'instType': 'SPOT', 
            'lever': '', 
            'ordId': '424583520932225029',
            'ordType': 'market', 
            'pnl': '0', 
            'posSide': 'net', 
            'px': '', 
            'rebate': '0', 
            'rebateCcy': 'USDT', 
            'side': 'buy', 
            'slOrdPx': '', 
            'slTriggerPx': '', 
            'slTriggerPxType': '', 
            'source': '', 
            'state': 'filled', 
            'sz': '0.001', 
            'tag': '', 
            'tdMode': 'cash', 
            'tgtCcy': 'base_ccy', 
            'tpOrdPx': '', 
            'tpTriggerPx': '', 
            'tpTriggerPxType': '', 
            'tradeId': '188054733', 
            'uTime': '1647500599894'
        }, 
        'id': '424583520932225029', 
        'clientOrderId': 'e847386590ce4dBC34e5fd928fb0b207', 
        'timestamp': 1647500599770, 
        'datetime': '2022-03-17T07:03:19.770Z', 
        'lastTradeTimestamp': 1647500599775, 
        'symbol': 'ETH/USDT', 
        'type': 'market',
        'timeInForce': 'IOC', 
        'postOnly': None, 
        'side': 'buy', 
        'price': 2751.21, 
        'stopPrice': None, 
        'average': 2751.21, 
        'cost': 2.75121, 
        'amount': 0.001, 
        'filled': 0.001, 
        'remaining': 0.0, 
        'status': 'closed', 
        'fee': 
        {
            'cost': 1e-06, 
            'currency': 'ETH'
        }, 
        'trades': [], 
        'fees': 
        [{
            'cost': 1e-06, 
            'currency': 'ETH'
        }]
    }
'''

'''
    fetch_order接口 市价卖成交返回的数据结构
    {
        'info': 
        {
            'accFillSz': '0.001', 
            'avgPx': '2751.04', 
            'cTime': '1647500622423', 
            'category': 'normal', 
            'ccy': '', 
            'clOrdId': 'e847386590ce4dBC7bd612cb9a889592', 
            'fee': '-0.00275104', 
            'feeCcy': 'USDT', 
            'fillPx': '2751.04', 
            'fillSz': '0.001', 
            'fillTime': '1647500622427',
            'instId': 'ETH-USDT', 
            'instType': 'SPOT', 
            'lever': '', 
            'ordId': '424583615945793536', 
            'ordType': 'market', 
            'pnl': '0', 
            'posSide': 'net', 
            'px': '', 
            'rebate': '0', 
            'rebateCcy': 'ETH', 
            'side': 'sell', 
            'slOrdPx': '', 
            'slTriggerPx': '', 
            'slTriggerPxType': '', 
            'source': '', 
            'state': 'filled', 
            'sz': '0.001', 
            'tag': '', 
            'tdMode': 'cash', 
            'tgtCcy': 'base_ccy', 
            'tpOrdPx': '', 
            'tpTriggerPx': '', 
            'tpTriggerPxType': '', 
            'tradeId': '188054782', 
            'uTime': '1647500622505'
        }, 
        'id': '424583615945793536', 
        'clientOrderId': 'e847386590ce4dBC7bd612cb9a889592', 
        'timestamp': 1647500622423, 
        'datetime': '2022-03-17T07:03:42.423Z', 
        'lastTradeTimestamp': 1647500622427, 
        'symbol': 'ETH/USDT', 
        'type': 'market', 
        'timeInForce': 'IOC', 
        'postOnly': None, 
        'side': 'sell', 
        'price': 2751.04, 
        'stopPrice': None, 
        'average': 2751.04, 
        'cost': 2.75104, 
        'amount': 0.001, 
        'filled': 0.001, 
        'remaining': 0.0, 
        'status': 'closed', 
        'fee': 
        {
            'cost': 0.00275104, 
            'currency': 'USDT'
        }, 
        'trades': [], 
        'fees': [
            {
                'cost': 0.00275104, 
                'currency': 'USDT'
            }]
    }

'''


'''
    fetch_order  挂单买成交返回接口数据结构
    {
        'info': 
        {
            'accFillSz': '0.001', 
            'avgPx': '2755.6', 
            'cTime': '1647503577459', 
            'category': 'normal', 
            'ccy': '', 
            'clOrdId': 'e847386590ce4dBC4124dc38296f8b85', 
            'fee': '-0.0000008', 
            'feeCcy': 'ETH', 
            'fillPx': '2755.6', 
            'fillSz': '0.001', 
            'fillTime': '1647503627732', 
            'instId': 'ETH-USDT', 
            'instType': 'SPOT', 
            'lever': '', 
            'ordId': '424596010265108482', 
            'ordType': 'limit', 
            'pnl': '0', 
            'posSide': 'net', 
            'px': '2755.6', 
            'rebate': '0', 
            'rebateCcy': 'USDT', 
            'side': 'buy', 
            'slOrdPx': '', 
            'slTriggerPx': '', 
            'slTriggerPxType': '', 
            'source': '', 
            'state': 'filled', 
            'sz': '0.001', 
            'tag': '', 
            'tdMode': 'cash', 
            'tgtCcy': '', 
            'tpOrdPx': '', 
            'tpTriggerPx': '', 
            'tpTriggerPxType': '', 
            'tradeId': '188061634', 
            'uTime': '1647503627735'
        }, 
        'id': '424596010265108482', 
        'clientOrderId': 'e847386590ce4dBC4124dc38296f8b85', 
        'timestamp': 1647503577459, 
        'datetime': '2022-03-17T07:52:57.459Z', 
        'lastTradeTimestamp': 1647503627732, 
        'symbol': 'ETH/USDT', 
        'type': 'limit', 
        'timeInForce': None, 
        'postOnly': None, 
        'side': 'buy', 
        'price': 2755.6, 
        'stopPrice': None, 
        'average': 2755.6, 
        'cost': 2.7556,
        'amount': 0.001, 
        'filled': 0.001, 
        'remaining': 0.0, 
        'status': 'closed', 
        'fee': 
        {
            'cost': 8e-07, 
            'currency': 'ETH'
        }, 
        'trades': [], 
        
        'fees': 
        [{
            'cost': 8e-07, 
            'currency': 'ETH'
        }]
    }

'''

'''
    fetch_order挂单卖成交数据结构
    {
        'info': 
        {
            'accFillSz': '0.001', 
            'avgPx': '2807', 
            'cTime': '1647523075618', 
            'category': 'normal', 
            'ccy': '', 
            'clOrdId': 'e847386590ce4dBC229012716888d9d5', 
            'fee': '-0.0022456', 
            'feeCcy': 'USDT', 
            'fillPx': '2807', 
            'fillSz': '0.001', 
            'fillTime': '1647523080488', 
            'instId': 'ETH-USDT', 
            'instType': 'SPOT', 
            'lever': '', 
            'ordId': '424677791471394819', 
            'ordType': 'limit', 
            'pnl': '0', 
            'posSide': 'net', 
            'px': '2807', 
            'rebate': '0', 
            'rebateCcy': 'ETH', 
            'side': 'sell', 
            'slOrdPx': '', 
            'slTriggerPx': '', 
            'slTriggerPxType': '', 
            'source': '', 
            'state': 'filled', 
            'sz': '0.001', 
            'tag': '', 
            'tdMode': 'cash', 
            'tgtCcy': '', 
            'tpOrdPx': '', 
            'tpTriggerPx': '', 
            'tpTriggerPxType': '', 
            'tradeId': '188116930', 
            'uTime': '1647523080491'
        }, 
        'id': '424677791471394819', 
        'clientOrderId': 'e847386590ce4dBC229012716888d9d5', 
        'timestamp': 1647523075618, 
        'datetime': '2022-03-17T13:17:55.618Z', 
        'lastTradeTimestamp': 1647523080488, 
        'symbol': 'ETH/USDT', 
        'type': 'limit', 
        'timeInForce': None, 
        'postOnly': None, 
        'side': 'sell', 
        'price': 2807.0, 
        'stopPrice': None, 
        'average': 2807.0, 
        'cost': 2.807, 
        'amount': 0.001, 
        'filled': 0.001, 
        'remaining': 0.0, 
        'status': 'closed', 
        'fee': 
        {
            'cost': 0.0022456, 
            'currency': 'USDT'
        }, 
        'trades': [], 
        'fees': 
        [{
            'cost': 0.0022456, 
            'currency': 'USDT'
        }]
    }
'''

'''
    cancel_order接口返回的数据
    {
        'info': {
            'clOrdId': 'e847386590ce4dBC9f39db9c328e3101', 
            'ordId': '424562251906048002', 
            'sCode': '0', 
            'sMsg': ''
            }, 
        'id': '424562251906048002', 
        'clientOrderId': 'e847386590ce4dBC9f39db9c328e3101', 
        'timestamp': None, 
        'datetime': None, 
        'lastTradeTimestamp': None, 
        'symbol': 'ETH/USDT', 
        'type': None, 
        'timeInForce': None, 
        'postOnly': None, 
        'side': None, 
        'price': None, 
        'stopPrice': None, 
        'average': None, 
        'cost': None, 
        'amount': None, 
        'filled': None, 
        'remaining': None, 
        'status': None, 
        'fee': None, 
        'trades': [], 
        'fees': []
    }

'''

'''
    fetch_order_fee
    {
        'info': 
        {
            'category': '1', 
            'delivery': '', 
            'exercise': '', 
            'instType': 'SPOT', 
            'isSpecial': '0', 
            'level': 'Lv1', 
            'maker': '-0.0008', 
            'taker': '-0.001', 
            'ts': '1647523654444'
        }, 
        'symbol': 'ETH/USDT', 
        'maker': -0.0008, 
        'taker': -0.001
    }
'''

'''#tick的数据结构
        {'symbol': 'ETH/USDT', 'timestamp': 1647441423571, 'datetime': '2022-03-16T14:37:03.571Z', 'high': 2734.0, 
         'low': 2554.55, 'bid': 2704.2, 'bidVolume': 0.680553, 'ask': 2704.21, 'askVolume': 4.899036, 'vwap': 2652.2203429610645,
         'open': 2559.34, 'close': 2703.33, 'last': 2703.33, 'previousClose': None, 'change': 143.99, 
         'percentage': 5.626059843553416, 'average': 2631.335, 'baseVolume': 143915.815408, 'quoteVolume': 381696453.298927, 
         'info': {'instType': 'SPOT', 'instId': 'ETH-USDT', 'last': '2703.33', 'lastSz': '0.016102', 'askPx': '2704.21', 
         'askSz': '4.899036', 'bidPx': '2704.2', 'bidSz': '0.680553', 'open24h': '2559.34', 'high24h': '2734', 
         'low24h': '2554.55', 'volCcy24h': '381696453.298927', 'vol24h': '143915.815408', 'ts': '1647441423571', 
         'sodUtc0': '2618.06', 'sodUtc8': '2572.4'}} 

'''
'''
        book的数据结构
        {'symbol': 'ETH/USDT', 
        'bids': [[2703.52, 38.400992], [2703.44, 0.5], [2703.34, 1.059], [2703.31, 0.45], [2703.26, 0.08], 
            [2703.19, 0.196868], [2703.06, 0.759998], [2703.05, 1.57285], [2703.0, 0.02], [2702.86, 0.140151], [2702.85, 0.073929], 
            [2702.84, 0.530684], [2702.83, 1.57285], [2702.81, 0.369868], [2702.8, 7.998], [2702.62, 25.098004], [2702.61, 0.001], 
            [2702.6, 0.02], [2702.5, 2.981411], [2702.45, 0.030063]], 
        'asks': [[2703.53, 8.585444], [2703.55, 0.102], [2703.59, 0.015], [2703.6, 0.02], [2703.64, 0.8], [2703.79, 0.005], 
            [2703.8, 0.02], [2704.0, 0.346528], [2704.08, 0.097794], [2704.2, 0.02], [2704.31, 0.00101], [2704.4, 0.044062], 
            [2704.41, 1.447598], [2704.53, 0.050822], [2704.54, 0.770617], [2704.59, 0.073969], [2704.6, 8.695778], [2704.62, 2.961],
            [2704.79, 0.08], [2704.8, 0.02]], 
        'timestamp': 1647441477510, 'datetime': '2022-03-16T14:37:57.510Z', 'nonce': None}
'''

#手续费扣除: 买扣币,卖扣u


'''
    fetch_open_orders
    [
        {
            'info': 
            {
                'accFillSz': '0', 
                'avgPx': '', 
                'cTime': '1647966732153', 
                'category': 'normal', 
                'ccy': '', 
                'clOrdId': '', 
                'fee': '0', 
                'feeCcy': 'NEAR', 
                'fillPx': '', 
                'fillSz': '0', 
                'fillTime': '', 
                'instId': 'NEAR-USDT', 
                'instType': 'SPOT', 
                'lever': '', 
                'ordId': '426538621850771459', 
                'ordType': 'limit', 
                'pnl': '0', 
                'posSide': 'net', 
                'px': '11.229', 
                'rebate': '0', 
                'rebateCcy': 'USDT', 
                'side': 'buy', 
                'slOrdPx': '', 
                'slTriggerPx': '', 
                'slTriggerPxType': '', 
                'source': '', 
                'state': 'live', 
                'sz': '0.5', 
                'tag': '', 
                'tdMode': 'cash', 
                'tgtCcy': '', 
                'tpOrdPx': '', 
                'tpTriggerPx': '', 
                'tpTriggerPxType': '', 
                'tradeId': '', 
                'uTime': '1647966732153'
            }, 
            'id': '426538621850771459', 
            'clientOrderId': None, 
            'timestamp': 1647966732153, 
            'datetime': '2022-03-22T16:32:12.153Z', 
            'lastTradeTimestamp': None, 
            'symbol': 'NEAR/USDT', 
            'type': 'limit', 
            'timeInForce': None, 
            'postOnly': None, 'side': 
            'buy', 
            'price': 11.229, 
            'stopPrice': None, 
            'average': None, 
            'cost': 0.0, 
            'amount': 0.5, 
            'filled': 0.0, 
            'remaining': 0.5, 
            'status': 'open', 
            'fee': {
                'cost': 0.0, 
                'currency': 'NEAR'
                }, 
            'trades': [], 
            'fees': [
                {
                    'cost': 0.0, 
                    'currency': 'NEAR'
                }]
        }, 
        {
            'info': 
            {
                'accFillSz': '0', 
                'avgPx': '', 
                'cTime': '1647966823939', 
                'category': 'normal', 
                'ccy': '', 
                'clOrdId': '', 
                'fee': '0', 
                'feeCcy': 'NEAR', 
                'fillPx': '', 
                'fillSz': '0', 
                'fillTime': '', 
                'instId': 'NEAR-USDT', 
                'instType': 'SPOT', 
                'lever': '', 
                'ordId': '426539006829158404', 
                'ordType': 'limit', 
                'pnl': '0', 
                'posSide': 'net', 
                'px': '11.229', 
                'rebate': '0', 
                'rebateCcy': 'USDT', 
                'side': 'buy', 
                'slOrdPx': '', 
                'slTriggerPx': '', 
                'slTriggerPxType': '', 
                'source': '', 
                'state': 'live', 
                'sz': '0.5', 
                'tag': '', 
                'tdMode': 'cash', 
                'tgtCcy': '', 
                'tpOrdPx': '', 
                'tpTriggerPx': '', 
                'tpTriggerPxType': '', 
                'tradeId': '', 
                'uTime': '1647966823939'
            }, 
            'id': '426539006829158404', 
            'clientOrderId': None, 
            'timestamp': 1647966823939, 
            'datetime': '2022-03-22T16:33:43.939Z', 
            'lastTradeTimestamp': None, 
            'symbol': 'NEAR/USDT', 
            'type': 'limit', 
            'timeInForce': None, 
            'postOnly': None, 
            'side': 'buy', 
            'price': 11.229, 
            'stopPrice': None, 
            'average': None, 
            'cost': 0.0, 
            'amount': 0.5, 
            'filled': 0.0, 
            'remaining': 0.5, 
            'status': 'open', 
            'fee': 
            {
                'cost': 0.0, 
                'currency': 'NEAR'
            }, 
            'trades': [], 
            'fees': [
                {
                    'cost': 0.0, 
                    'currency': 'NEAR'
                }
                ]
        }
    ]
'''

'''
    order_list
    委托表,按照价格排序
    {
        'price1':{
            'id':'1',
            'side':'buy',
            'qty': 1.1
        },
        'price2':{
            'id':'2',
            'side':'sell',
            'qty':1.2
        }
    }
'''

'''
    grid_list
    手数表,按照价格排序
    [
        {
            'price':1
            'buyqty':1,
            'sellqty':0.8
        },
        {
            'price':2
            'buyqty':2,
            'sellqty':0.8
        }
    ]
'''

class GridTrader():
    def __init__(self,file):
        if len(file) == 0:
            file='config.json'
        self.file=file
        self.start=True
        self.side=['buy','sell']
        self.type=['market','limit']
        self.exchange_list=['okex','ftx']
        self.has_qty=0

        #[[每格价格,每格需要买的币,每格能卖的币]]
        self.grid_list=[]
        
        #委托表
        self.order_dict={}

    @atexit.register
    def __del__(self):
        self.start=False
        
        #挂单撤销
        for  _,value in self.order_dict.items():
            id=value['id']
            self.log(f'程序结束,将挂单{id}撤掉')
            self.cancel_order(id,self.api_symbol)
        del self.order_dict

        #市价卖出所有持仓
        if self.has_qty >0:
            order=self.create_order(self.type[0],self.side[1],self.has_qty)
            if order!=None:
                self.log(f'程序结束,将所有持仓清仓,手数:{self.has_qty}')
            else:
                self.log('程序结束,所有持仓清仓失败')
            
            #order=self.create_order(self.side[1],self.has_qty)

    def init(self):
        # 读取配置文件
        self.read_config(self.file)

        # 交易所连接
        if(self.api_exchange=='okex'):
            self.exchange=ccxt.okex({
                'enableRateLimit': True,
                'apiKey': self.api_apikey,
                'secret':self.api_secret,
                'password':self.api_passwd,
            })
        elif self.api_exchange=='ftx':
            self.exchange=ccxt.ftx({
                'enableRateLimit': True,
                'apiKey': self.api_apikey,
                'secret':self.api_secret,
            })
        else:
            self.log(f'不支持此交易所,{self.api_exchange}')
            return False

        #获取账号手续费
        self.get_account_fee()

        #计算出每格的毛利润,数据不变
        self.ratio_per_grid=(self.grid_upbound/self.grid_lowbound)**(1/self.grid_gridqty)-1
        self.log(f'每格毛利润率:{self.ratio_per_grid}')

        #计算出每格资金,数据不变
        self.fund_per_grid=self.grid_ammount/self.grid_gridqty
        self.fund_per_grid=GridTrader.cut(self.fund_per_grid,self.api_pricereserve)
        self.log(f"每格资金:{self.fund_per_grid}")

        #计算出每格的纯利润,数据不变
        self.net_profit=((1+self.grid_maker)**2)*(1+self.ratio_per_grid)-1
        self.log(f'每格纯利润:{self.net_profit}')

        #计算网格价格列表
        self.calc_grid_list()

        #获取最新的价格
        last = self.exchange.fetch_ticker(self.api_symbol)['last']
        while last < self.grid_list[0]['price'] or last>self.grid_list[-1]['price']:
            self.log('价格没在网格区间')
            last=self.exchange.fetch_ticker(self.api_symbol)['last']
            time.sleep(self.api_timeinterval)

        #获取当前价格所在编号
        self.current_gridno=self.get_current_grid_no(last)
        
        qty=0
        index=0
        for index in range(self.current_gridno+1, len(self.grid_list)):
            qty+= self.grid_list[index]['buyqty']

        qty=GridTrader.cut(qty,self.api_qtyreserve)
        
        self.log(f'当前价格:{last},所在网格:{self.current_gridno},需要开单手数:{qty}')
        
        book=self.exchange.fetch_order_book(self.api_symbol)
        max_price=last*(1+self.grid_slip)
        #计算出在滑点范围内的深度
        qty_depth=0
        for price_pair in book['asks']:
            if(price_pair[0]<max_price):
                qty_depth=qty_depth+price_pair[1]
        
        if qty_depth > qty:
            #深度足够
            order=self.create_order(self.type[0],self.side[0],qty)
            if order!=None:
                self.log(f'深度足够,开市价进场,委托为:{order}')
                while True:
                    order_ret,flag=self.check_order_finish(order['id'])
                    if order_ret!=None and flag==True:
                        return True
                    else:
                        id=order['id']
                        self.log(f'开仓单{id}未成交,{order_ret},{flag}')
                        time.sleep(1)
                        continue
            else:
                return False
        else:
            #深度不够,当前价挂单
            self.log(f'深度不够,开限价进场')
            order=self.create_order(self.type[1],self.side[0],qty,last)
            if order!=None:
                while True:
                    order,flag=self.check_order_finish(order['id'])
                    if order!=None and flag==True:
                        return True
                    else:
                        id=order['id']
                        self.log(f'开仓单{id}未成交,{order},{flag}')
                        time.sleep(1)
                        continue
            return False
                    
    def get_current_grid_no(self,last):
        index=0

        #价格跌破网格
        if self.grid_list[0]['price'] >= last:
            return -1

        #价格涨破网格
        if self.grid_list[-1]['price'] <= last:
            return -1
        

        for index in range(len(self.grid_list)-1):
            if self.grid_list[index +1]['price'] >last and self.grid_list[index]['price'] <last:
                return index
        
    #补网格
    # def update_grid(self,last):
    #     for index in range(len(self.grid_list)):
    #         price= self.grid_list[index]['price']
    #         order_value = self.order_dict.get(f'{price}')
    #         if order_value == None:
    #             #在委托表里没找到网格价格,需要对这个价格进行补充委托
    #             if last > price:
    #                 #最新价 大于 网格价,挂买单
    #                 buyqty=self.grid_list[index]['buyqty']
    #                 order=self.create_order(self.type[1],self.side[0],buyqty,price)
    #                 if order != None:
    #                     self.order_dict[f'{price}']=dict([('id',order['id']),('side',self.side[0]),('qty',buyqty)])
    #             elif last < price:
    #                 #最新价 小于 网格价,挂卖单
    #                 sellqty=self.grid_list[index]['sellqty']
    #                 order=self.create_order(self.type[1],self.side[1],sellqty,price)
    #                 if order != None:
    #                     self.order_dict[f'{price}']=dict([('id',order['id']),('side',self.side[1]),('qty',sellqty)])


    def create_order(self,type,side,qty,price=None):
        try:
            order = self.exchange.create_order(self.api_symbol,type,side,qty,price)
            id=order['id']
            self.log_order(f'open,success,{self.api_symbol},{id},{type},{side},{price},{qty}')
            return order
        except Exception as e:
            strmsg=self.err_paser(e)
            self.log_order(f'open,fail:{strmsg},{self.api_symbol},,{type},{side},{price},{qty}')
            self.log(f'创建委托失败,品种:{self.api_symbol},委托类型:{type},方向:{side},价格:{price},手数:{qty},错误:{strmsg}')
            return None
    
    def cancel_order(self,id):
        try:
            self.exchange.cancel_order(id,self.api_symbol)
            self.log_order(f'cancel,success,{self.api_symbol},{id}')
        except Exception as e:
            strmsg=self.err_paser(e)
            self.log_order(f'cancel,fail:{strmsg},{self.api_symbol},{id}')
            self.log(f"撤单失败,订单号:{id},失败原因:{strmsg}")
    
    def check_order_finish(self,id):
        try:
            order=self.exchange.fetch_order(id,self.api_symbol)
            if order==None:
                return 
            if order['status']=='closed':
                #记录持有手数
                if order['side'] ==self.side[0]:
                    self.buy_trade(order)
                else:
                    self.sell_trade(order)

                #开单手数减去手续费扣得币
                qty=float(order['filled'])
                fee=0
                if order['fee']!=None and order['fee']['cost']!=None:
                    fee = float(order['fee']['cost'])
                side=order['side']
                price=float(order['price'])
                currency=''
                if order['fee']!=None and order['fee']['currency']!=None:
                    currency=order['fee']['currency']
                id=order['id']
                type=order['type']
                self.log_order(f'closed,success,{self.api_symbol},{id},{type},{side},{price},{qty},{currency},{fee}')
                return order,True
            return order,False
        except Exception as e:
            emsg=self.err_paser(e)
            self.log(f'委托查询错误,错误信息为:{emsg}')
            return None,False


    
    def create_grid(self):
        self.log(f'开启网格')
        has_qty=self.has_qty
        for index in range(len(self.grid_list)):
            if index <= self.current_gridno:
                #比当前价所在的网格低的开买单
                price= self.grid_list[index]['price']
                qty=self.grid_list[index]['buyqty']
                order = self.create_order(self.type[1],self.side[0],qty,price)
                if order!=None:
                    self.order_dict[f'{price}']=dict([('id',order['id']),('side',self.side[0]),('qty',qty)])
                    self.log(f'网格创建成功,网格编号为{index},方向为{self.side[0]},网格下沿价格为{price},挂单手数{qty}')
            
            elif index >self.current_gridno:
                #比当前价所在的网格高的开卖单
                price= self.grid_list[index]['price']
                qty=self.grid_list[index]['sellqty']
                if(has_qty < qty):
                    qty=has_qty
                    self.grid_list[index]['sellqty']=qty
                order = self.create_order(self.type[1],self.side[1],qty,price)
                if order!=None:
                    self.order_dict[f'{price}']=dict([('id',order['id']),('side',self.side[0]),('qty',qty)])
                    self.log(f'网格创建成功,网格编号为{index},方向为{self.side[1]},网格下沿价格为{price},挂单手数{qty}')
                    has_qty=has_qty-qty
            time.sleep(0.2)

    def grid_start(self):
        self.create_grid()
        three_hours_num=int((60*60*3)/self.api_timeinterval)
        thrity_miutes_num=int((60*30)/self.api_timeinterval)
        ten_second_num=int(10/self.api_timeinterval)
        i =0
        while self.start:

            #更新手续费,大概每隔三小时更新一次
            if(++i >=three_hours_num):
                i=0
                self.get_account_fee()
            
            #每半小时更新一次委托表
            # if i%thrity_miutes_num==0:
            #     self.update_all_orders()

            last=0.0
            try:
                last=self.exchange.fetch_ticker(self.api_symbol)['last']
            except:
                continue

            #检测委托表
            self.update_all_orders2(last)

            #每隔十秒钟维护一次委托表
            # if i%ten_second_num==0:
            #     self.update_grid(last)

            #价格已经到了止损线,止损退出
            if last<self.grid_stop:
                self.log(f'已向下突破止损线,{self.api_symbol}的当前价格为{last},止损价格为{self.grid_stop}')
                self.stop_grid()
                break
            
            # self.price_check2(last)

            # self.update_order(last)

            time.sleep(self.api_timeinterval)

    #获取账号手续费
    def get_account_fee(self):
        if self.api_exchange==self.exchange_list[0]:
            self.get_okex_trading_fee()
        elif self.api_exchange==self.exchange_list[1]:
            self.get_ftt_trading_fee()
    
    def get_okex_trading_fee(self):
        try:
            fee=self.exchange.fetch_trading_fee(self.api_symbol)
            #限手续费,是扣币
            self.grid_maker=fee['maker']
            #市价手续费,是扣u
            self.grid_taker=fee['taker']
            self.log(f'限价手续费:{self.grid_maker},市价手续费:{self.grid_taker}')
        except:
            pass
    
    def get_ftt_trading_fee(self):
        self.grid_maker=0
        self.grid_taker=0

    # def price_check2(self,last):
    #     #获取当前价格网格编号
    #     current_gridno = self.get_current_grid_no(last)
    #     if current_gridno == -1:
    #         #价格突破天地阁
    #         return

    #     if current_gridno>self.current_gridno:
    #         breakthrough_grid=current_gridno-self.current_gridno
    #         self.log(f'网格向上突破,之前价格所在网格:{self.current_gridno},现在价格所在网格编号:{current_gridno},突破网格数{breakthrough_grid}')
    #         #价格涨上去了,买网格
    #         for index in range(self.current_gridno+1,current_gridno+1):
    #             price=self.grid_list[index]['price']
    #             #根据价格找委托
    #             order_info=self.order_dict.get(f'{price}')
    #             if order_info == None:
    #                 #买单,手数=每格金钱/每格下沿价格
    #                 qty=self.grid_list[index]['buyqty']
    #                 order= self.create_order(self.api_symbol,self.type[1],self.side[0], qty,price)
    #                 if order !=None:
    #                     order_id=order['id']
    #                     self.log(f'挂买单,价格为{price},数量为{qty},委托编号{order_id}')
    #                     self.order_dict[f'price']=dict([('id',order_id),('side',self.side[0]),('qty',qty)])
                    
    #         self.current_gridno=current_gridno
    #     elif current_gridno < self.current_gridno:
    #         breakthrough_grid=self.current_gridno-current_gridno
    #         self.log(f'网格向下突破,之前价格所在网格:{self.current_gridno},现在价格所在网格编号:{current_gridno},突破网格数{breakthrough_grid}')
    #         #价格跌下去了,挂卖单
    #         for index in range(current_gridno+1,self.current_gridno+1):
    #             price=self.grid_list[index]['price']
    #             #根据 价格找委托
    #             order_info=self.order_dict.get(f'{price}')
    #             if order_info == None:
    #                 #卖单手数=每格金钱/每格下沿价格*(1-手续费)
    #                 qty= self.grid_list[index]['sellqty']
    #                 order= self.exchange.create_order(self.api_symbol,self.type[1],self.side[1], qty,price)
    #                 order_id=order['id']
    #                 self.log(f'挂卖单,价格为{price},数量为{qty},委托编号{order_id}')
    #                 self.order_dict[f'{price}']=dict([('id',order_id),('side',self.side[0]),('qty',qty)])
            
    #         self.current_gridno=current_gridno

    #止损
    def stop_grid(self):
        #将所有挂单清掉
        for  _,value in self.order_dict.items():
            id=value['id']
            self.cancel_order(id)
            self.log(f'程序结束,将挂单{id}撤掉')
        del self.order_dict
        
        #将所持有手数全在止损价挂卖单
        if self.has_qty >0:
            order=self.create_order(self.type[1],self.side[1],self.has_qty,self.grid_stop)
            #self.create_order(self.side[1],self.has_qty,self.grid_stop)
            
    #更新挂单表,将已成交的挂单删除,并记录现在持有数量
    # def update_order(self,last):
    #     for price in list(self.order_dict):
    #         order=self.order_dict[f'{price}']
    #         if float(price) > last and order['side']==self.side[0]:
    #             #委托单位买,且买价大于等于最新价,表示挂单已成交,更新委托信息
    #             info,flag =self.check_order_finish(order['id'])
    #             if info!=None and flag==True:
    #                 self.buy_trade(info)
    #                 self.order_dict.pop(price)
    #                 continue
    #         elif float(price) < last and order['side']==self.side[1]:
    #             #委托单为卖,且卖价小于等于最新价,表示挂单或已成交,更新委托信息
    #             info,flag=self.check_order_finish(order['id'])
    #             if info!=None and flag==True:
    #                 self.sell_trade(info)
    #                 self.order_dict.pop(price)
    #                 continue
    
    #更新挂单表
    def update_all_orders2(self,last):
        try:
            order_list=self.exchange.fetch_open_orders(symbol=self.api_symbol)
            price_list=[]
            for order in order_list:
                price_list.append(order['price'])
            
            for price in list(self.order_dict):
                f_price=float(price)
                grid_data=self.get_grid_by_price(f_price)
                if grid_data==None:
                    continue
                if f_price not in price_list:
                    #委托列表里没找到这个档位的委托,表示这个价位挂单已成交
                    #将委托表里的单子处理掉
                    order=self.order_dict[price]
                    
                    #这里再检查一次委托,如果完全成交才接着挂单
                    info,flag=self.check_order_finish(order['id'])
                    if info == None or flag==False:
                        continue

                    #接着挂单
                    if f_price >last:
                        #网格价格比当前价高,挂卖单
                        order=self.create_order(self.type[1],self.side[1],grid_data['sellqty'],f_price)
                        if order !=None:
                            self.order_dict[f'{price}']=dict([('id',order['id']),('side',self.side[1]),('qty',grid_data['sellqty'])])
                    if f_price<last:
                        order=self.create_order(self.type[1],self.side[0],grid_data['buyqty'],f_price)
                        if order !=None:
                            self.order_dict[f'{price}']=dict([('id',order['id']),('side',self.side[1]),('qty',grid_data['buyqty'])])
        except Exception as e:
            err_msg=self.err_paser(e)
            self.log(f'批量查挂单失败,失败原因:{err_msg}')

            
    
    #根据价格查找网格数据
    def get_grid_by_price(self,price):
        for index in range(len(self.grid_list)):
            if self.grid_list[index]['price'] == price:
                return self.grid_list[index]
        return None

    #将全部委托查一遍,更新委托表
    # def update_all_orders(self):
    #     for price in list(self.order_dict):
    #         order=self.order_dict[f'{price}']
    #         info,flag=self.check_order_finish(order['id'])
    #         if info==None or flag==False:
    #             continue
    #         if info['side']==self.side[0]:
    #             self.buy_trade(info)
    #             self.order_dict.pop(price)
    #         else:
    #             self.sell_trade(info)
    #             self.order_dict.pop(price)
    #         time.sleep(0.2)

    def buy_trade(self,info):
        fill=0.0
        if info['fee']==None:
            fill=info['filled']
        else:
            if info['fee']['cost'] !=None:
                fill=float(info['filled']-float(info['fee']['cost']))
        self.has_qty=self.has_qty+fill
        id=info['id']
        price=info['price']
        self.log(f'网格挂单成交,委托号为:{id},方向为:{self.side[0]},成交手数(扣除手续费)为:{fill},委托价格为:{price},委托为:{info}')

    def sell_trade(self,info):
        fill=info['filled']
        price=info['price']
        self.has_qty=self.has_qty-fill
        id=info['id']
        self.log(f'网格挂单成交,委托号为:{id},方向为:{self.side[1]},成交手数为:{fill},委托价格为:{price},委托为:{info}')
                   
    
    #根据网格设置计算出所有的网格价格,保留小数点后6位
    def calc_grid_list(self):
        strr='网格价格'
        for i in range(0,self.grid_gridqty):
            price= GridTrader.cut(self.grid_lowbound*(1+self.ratio_per_grid)**(i),self.api_pricereserve)
            #每格能买的手数=每格金钱/每格下沿价格
            qty=GridTrader.cut(self.fund_per_grid/price,self.api_qtyreserve)
            #每格扣完手续费能买的手数=(每格金钱/每格下沿价格)*(1-市价手续费)
            qty2= GridTrader.cut(self.fund_per_grid/price*(1+self.grid_taker),self.api_qtyreserve)
            self.grid_list.append(dict([('price',price),('buyqty',qty),('sellqty',qty2)]))
            strr+= f'网格编号:{i},网格下沿价格:{price},在此网格需要买的币:{qty},此格扣完手续费之后能得到的币:{qty2} '
        self.log(f'{strr}')
        
    def read_config(self,file='config.ini'):
        #读取配置文件
        cfg=configparser.ConfigParser()
        try:
            cfg.read(file)
        except Exception as e:
            estr=str(e)
            self.log(f'配置文件未找到,{estr}')
            return

        #基础配置
        self.gl_logfile=cfg.get('global','logfile')

        self.gl_orderfile=cfg.get('global','orderfile')

        #mysql配置
        # self.sql_database=cfg.get('mysql','database')
        # self.sql_table=cfg.get('mysql','table')
        # self.sql_host=cfg.get('mysql','host')
        # self.sql_port=cfg.get('mysql','port')
        # self.sql_user=cfg.get('mysql','user')
        # self.sql_passwd=cfg.get('mysql','passwd')

        #api配置
        self.api_exchange=cfg.get('api','exchange').lower()
        if self.api_exchange != 'okex' and self.api_exchange != 'ftx':
            raise Exception('交易所设置错误,目前只支持OKEX或者FTX',self.api_exchange)

        self.api_apikey=cfg.get('api','apikey')
        if len(self.api_apikey)==0:
            raise Exception('APIKEY不能为空')

        self.api_secret=cfg.get('api','secret')
        if len(self.api_secret)==0:
            raise Exception('APISECRET不能为空')

        self.api_symbol=cfg.get('api','symbol')
        if len(self.api_symbol)==0:
            raise Exception('交易品种不能为空')

        self.api_passwd=cfg.get('api','passwd')
        # if len(self.api_passwd)==0:
        #     raise Exception('密码不能为空')

        self.api_timeinterval=cfg.getfloat('api','time_interval')
        if self.api_timeinterval<=0:
            raise Exception('操作时间间隔不能小于等于0')

        #网格配置
        try:
            self.api_pricereserve=cfg.getint('api','price_reserve')
            if(self.api_pricereserve<0 or self.api_pricereserve>8):
                raise Exception('价格小数后保留位数设置错误',self.api_pricereserve)
            
            self.api_qtyreserve=cfg.getint('api','qty_reserve')
            if(self.api_qtyreserve<0 or self.api_qtyreserve>8):
                raise Exception('手数小数后保留位数设置错误',self.api_qtyreserve)

            self.grid_upbound=cfg.getfloat('grid','upbound')
            if (self.grid_upbound <=0):
                raise Exception('天阁设置错误,',self.grid_upbound)
            
            self.grid_lowbound=cfg.getfloat('grid','lowbound')
            if(self.grid_lowbound <= 0):
                raise Exception('地阁设置错误',self.grid_lowbound)
            
            if(self.grid_upbound <= self.grid_lowbound):
                raise Exception('天地阁设置错误,天阁 %f, 地阁 %f',self.grid_upbound,self.grid_lowbound)

            self.grid_gridqty=cfg.getint('grid','gridqty')
            if(self.grid_gridqty <=0):
                raise Exception('网格设置错误',self.grid_gridqty)

            self.grid_ammount=cfg.getfloat('grid','ammount')
            if(self.grid_ammount <=0):
                raise Exception('资金设置错误',self.grid_ammount)

            self.grid_stop=cfg.getfloat('grid','stop')
            if(abs(self.grid_stop) < sys.float_info.epsilon): 
                raise Exception('止损价设置错误',self.grid_stop)
            
            if(self.grid_stop > self.grid_lowbound):
                raise Exception(f'止损价不能大于地格,止损价:{self.grid_stop},地格:{self.grid_lowbound}')

            
            self.grid_slip=cfg.getfloat('grid','slip')
            if(self.grid_slip <0):
                raise Exception('滑点设置错误',self.grid_slip)

        except Exception as e:
            self.log(str(e))
            raise

    def log(self,msg,withTime=True):
        timestamp=datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%b %d %Y %H:%M:%S, ")
        try:
            f=open(f"{self.gl_logfile}",'a')
            if withTime:
                f.write(timestamp+msg+"\n")
            else:
                f.write(msg+"\n")
            f.close()
        except:
            pass

    def log_order(self,msg):
        timestamp=datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%b %d %Y %H:%M:%S, ")
        try:
            f=open(f"{self.gl_orderfile}",'a')
            f.write(timestamp+msg+"\n")
            f.close()
        except:
            pass

    def err_paser(self,e):
        if self.api_exchange==self.exchange_list[0]:
            return GridTrader.okex_err_paser(e)
        elif self.api_exchange==self.exchange_list[1]:
            return GridTrader.ftx_err_paser(e)
        else:
            return ''
    
    @staticmethod
    def okex_err_paser(e):
        strr=str(e)
        strr1=strr[strr.find('{'):]
        try:
            json_data=json.loads(strr1)
            return json_data['data'][0]['sMsg']
        except:
            return strr
    
    @staticmethod
    def ftx_err_paser(e):
        strr=str(e)
        strr1=strr[strr.find('{'):]
        try:
            str_json=json.loads(strr1)
            return str_json['error']
        except:
            return strr
    
    @staticmethod
    def cut(f,n):
        return float(int(f*10**n)/10**n)

if __name__ == '__main__':
    file=''
    if len(sys.argv) > 1:
        file=f'{sys.argv[1]}'
    grid_trader=GridTrader(f'{file}')
    if grid_trader.init() == True:
        grid_trader.grid_start()