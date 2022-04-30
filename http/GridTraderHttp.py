from ast import ExceptHandler
from datetime import datetime
from multiprocessing.spawn import get_preparation_data
from attr import has
import ccxt 
import time 
# import configparser
import pytz
# import math
import sys
# import atexit
import json
import threading
sys.path.append('..')
from common import obj_to_json

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

'''
    fetch_balance
    {
        'info': 
        {
            'code': '0', 
            'data': 
            [
                {
                    'adjEq': '', 
                    'details': 
                    [
                        {
                            'availBal': '188.89702391651866', 
                            'availEq': '', 
                            'cashBal': '188.89702391651866', 
                            'ccy': 'USDT', 
                            'crossLiab': '', 
                            'disEq': '188.94802611297612', 
                            'eq': '188.89702391651866', 
                            'eqUsd': '188.94802611297612', 
                            'frozenBal': '0', 
                            'interest': '', 
                            'isoEq': '', 
                            'isoLiab': '', 
                            'isoUpl': '', 
                            'liab': '', 
                            'maxLoan': '', 
                            'mgnRatio': '', 
                            'notionalLever': '', 
                            'ordFrozen': '0', 
                            'stgyEq': '0', 
                            'twap': '0', 
                            'uTime': '1649827304063', 
                            'upl': '', 
                            'uplLiab': ''
                        }, 
                        {
                            'availBal': '0.0000962', 
                            'availEq': '', 
                            'cashBal': '0.0000962', 
                            'ccy': 'ETH', 
                            'crossLiab': '', 
                            'disEq': '0.293821736', 
                            'eq': '0.0000962', 
                            'eqUsd': '0.293821736', 
                            'frozenBal': '0', 
                            'interest': '', 
                            'isoEq': '', 
                            'isoLiab': '', 
                            'isoUpl': '', 
                            'liab': '', 
                            'maxLoan': '', 
                            'mgnRatio': '', 
                            'notionalLever': '', 
                            'ordFrozen': '0', 
                            'stgyEq': '0', 
                            'twap': '0', 
                            'uTime': '1647577616616', 
                            'upl': '', 'uplLiab': ''
                        }, 
                        {
                            'availBal': '0.0000008584', 
                            'availEq': '', 
                            'cashBal': '0.0000008584', 
                            'ccy': 'AAVE', 
                            'crossLiab': '', 
                            'disEq': '0.0001237791182054', 
                            'eq': '0.0000008584', 
                            'eqUsd': '0.0001456224920064', 
                            'frozenBal': '0', 
                            'interest': '', 
                            'isoEq': '', 
                            'isoLiab': '', 
                            'isoUpl': '', 
                            'liab': '', 
                            'maxLoan': '', 
                            'mgnRatio': '', 
                            'notionalLever': '', 
                            'ordFrozen': '0', 
                            'stgyEq': '0', 
                            'twap': '0', 
                            'uTime': '1649771621399', 
                            'upl': '', 'uplLiab': ''
                        }, 
                        {
                            'availBal': '0.000000003914', 
                            'availEq': '', 
                            'cashBal': 
                            '0.000000003914', 
                            'ccy': 'NEAR', 
                            'crossLiab': '', 
                            'disEq': '0.0000000543123079', 
                            'eq': '0.000000003914', 
                            'eqUsd': '0.0000000638968328', 
                            'frozenBal': '0', 
                            'interest': '', 
                            'isoEq': '', 
                            'isoLiab': '', 
                            'isoUpl': '', 
                            'liab': '', 
                            'maxLoan': '', 
                            'mgnRatio': '', 
                            'notionalLever': '', 
                            'ordFrozen': '0', 
                            'stgyEq': '0', 
                            'twap': '0', 
                            'uTime': '1649827304063', 
                            'upl': '', 
                            'uplLiab': ''
                        }], 
                        'imr': '', 
                        'isoEq': '', 
                        'mgnRatio': '', 
                        'mmr': '', 
                        'notionalUsd': '', 
                        'ordFroz': '', 
                        'totalEq': '189.24199353536497', 
                        'uTime': '1649827752951'
                    }
                ], 
                'msg': ''
            }, 
        'USDT': 
        {
            'free': 188.89702391651866, 
            'used': 0.0, 
            'total': 188.89702391651866
        }, 
        'ETH': 
        {
            'free': 9.62e-05, 
            'used': 0.0, 
            'total': 9.62e-05
        },
        'AAVE': 
        {
            'free': 8.584e-07, 
            'used': 0.0, 
            'total': 8.584e-07
        }, 
        'NEAR': 
        {
            'free': 3.914e-09, 
            'used': 0.0, 
            'total': 3.914e-09
        }, 
        'timestamp': 1649827752951, 
        'datetime': '2022-04-13T05:29:12.951Z', 
        'free': 
        {
            'USDT': 188.89702391651866, 
            'ETH': 9.62e-05, 
            'AAVE': 8.584e-07, 
            'NEAR': 3.914e-09
        }, 
        'used': 
        {
            'USDT': 0.0, 
            'ETH': 0.0, 
            'AAVE': 0.0, 
            'NEAR': 0.0
        }, 
        'total': 
        {
            'USDT': 188.89702391651866, 
            'ETH': 9.62e-05, 
            'AAVE': 8.584e-07, 
            'NEAR': 3.914e-09
        }
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
'''
    grid_list2
    网格表
    {
        'LowPrice':,
        'UpPrice':,
        'BuyQty':,
        'SellQty':,
        'Order':,
    }
'''

class GridTraderHttp():
    def __init__(self):
        self.start_flag=True
        self.side=['buy','sell']
        self.type=['market','limit']
        self.exchange_list=['okex','ftx']
        self.has_qty=0
        self.buy_num=0
        self.sell_num=0
        self.lock=threading.Lock()

        #[[每格价格,每格需要买的币,每格能卖的币]]
        self.grid_list=[]
        
        #委托表
        self.order_dict={}

    def __del__(self):
        self.start_flag=False
        
        #挂单撤销
        for  _,value in self.order_dict.items():
            id=value['id']
            self.log(f'程序结束,将挂单{id}撤掉')
            self.cancel_order(id,self.api_symbol)
        del self.order_dict
    

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

    @staticmethod
    def grid_calc(api,data):
        #登录
        exchange={}
        if(data['Exchange']=='okex'):
            exchange=ccxt.okex({
                'enableRateLimit': True,
                'apiKey': api['ApiKey'],
                'secret':api['Secret'],
                'password':api['Password'],
            })
        elif data['Exchange'] =='ftx':
            subaccount=api.get('Subaccount')
            if subaccount == None:
                exchange=ccxt.ftx({
                    'enableRateLimit': True,
                    'apiKey': api['ApiKey'],
                    'secret':api['Secret'],
                })
            else:
                exchange=ccxt.ftx({
                    'enableRateLimit': True,
                    'apiKey': api['ApiKey'],
                    'secret':api['Secret'],
                    'headers': {
                        'FTX-SUBACCOUNT': subaccount,
                    },
                })
        else:
            ex_name=data['Exchange']
            return False,f'选择的交易所{ex_name}不支持',{}

        #检测交易所是否连接成功
        grid_maker=0
        grid_taker=0
        try:
            fee=exchange.fetch_trading_fee(data['Symbol'])
            if data['Exchange']=='okex':
                #限手续费,是扣币
                grid_maker=abs(fee['maker'])
                #市价手续费,是扣u
                grid_taker=abs(fee['taker'])
            elif data['Exchange']=='ftx':
                grid_maker=0
                grid_taker=0
        except Exception as e:
            strr= str(e)
            return False,f'交易所连接失败:{strr}',{}

        #计算数据
        #计算出每格的毛利润,数据不变
        up_bound=float(data['UpBound'])
        low_bound=float(data['LowBound'])
        grid_qty=int(data['GridQty'])
        ammount=float(data['Ammount'])

        try:
            balance=exchange.fetch_balance()
            usdt=float(balance['total']['USDT'])
            if usdt<ammount:
                return False,f'账户余额比网格设置金额要小,账户余额{usdt}',{}
        except Exception as e:
            strr=str(e)
            return False,f'交易所连接失败:{strr}',{}
        

        price_reserve=int(data['PriceReserve'])
        ratio_per_grid=(up_bound/low_bound)**(1/grid_qty)-1
        
        #计算出每格资金,数据不变
        fund_per_grid=ammount/grid_qty
        fund_per_grid=GridTraderHttp.cut(fund_per_grid,price_reserve)

        #计算出每格的纯利润,数据不变
        net_profit=((1+grid_maker)**2)*(1+ratio_per_grid)-1

        #创建网格
        grid_list=GridTraderHttp.create_grid_list(ratio_per_grid,grid_taker,fund_per_grid,data)
        #print(str(grid_list))
        #获取当前价
        ticker={}
        last=0.0
        timestamp=0
        open = float(data['Open'])
        if open > sys.float_info.epsilon:  #设置了开仓价
            last=open
            timestamp=int(round(time.time() * 1000))
        else:
            try:
                ticker = exchange.fetch_ticker(data['Symbol'])
            except:
                return False,f'交易所连接失败,获取最新价格失败',{}
            last=ticker['last']

            if last<low_bound or last>up_bound:
                return False,f'最新行情不在网格天地格价格区间之内,最新价格为{last}',{}
            timestamp=ticker['timestamp']

        qty=0
        cost_ammount=0
        for i in grid_list:
            grid=i
            if grid['LowPrice']>last:
                #网格的下沿价格大于当前价,表示此格需要买入
                #需要买入的手数为每格相加
                #需要花费的金额为每格金额相加
                qty=qty+grid['BuyQty']
                cost_ammount=cost_ammount+fund_per_grid
        
        #剩余的金额=总金额-花费的金额
        remaining=ammount-cost_ammount

        #扣除手续费之后的净手数=手数*(1-市价手续费)
        net_qty=qty*(1-grid_taker)

        return True,'OK',dict([
            ('Id',''),
            ('Time',timestamp),
            ('RatioPerGrid',ratio_per_grid),
            ('FundPerGrid',fund_per_grid),
            ('ProFitPerGrid',ratio_per_grid),
            ('NetProfitPerGrid',net_profit),
            ('LastPrice',last),
            ('GridPriceList',GridTraderHttp.get_grid(grid_list)),
            ('EntryQty',qty),
            ('NetEntryQty',net_qty),
            ('AmountSpent',cost_ammount),
            ('RemainingAmount',remaining)
            ])

    @staticmethod
    def get_grid(grid_list):
        grid_list_meta=[]
        for  item in grid_list:
            grid_list_meta.append(dict([
                ('LowPrice',item['LowPrice']),
                ('UpPrice',item['UpPrice']),
                ('BuyQty',item['BuyQty']),
                ('SellQty',item['SellQty'])
            ]))
        return grid_list_meta

    def start(self):
        #交易所连接
        if self.api_exchange=='okex':
            self.exchange=ccxt.okex({
                'enableRateLimit': True,
                'apiKey': self.api_apikey,
                'secret':self.api_secret,
                'password':self.api_passwd,
            })
        elif self.api_exchange =='ftx':
            self.exchange=ccxt.ftx({
                'enableRateLimit': True,
                'apiKey': self.api_apikey,
                'secret':self.api_secret,
            })

        #取得手续费
        self.get_account_fee()
        
        #每格利润
        self.ratio_per_grid=(self.grid_upbound/self.grid_lowbound)**(1/self.grid_gridqty)-1
        
        #计算出每格资金,数据不变
        fund_per_grid=self.grid_ammount/self.grid_gridqty
        fund_per_grid=GridTraderHttp.cut(fund_per_grid,self.api_pricereserve)

        #计算出每格的纯利润,数据不变
        net_profit=((1+self.grid_maker)**2)*(1+self.ratio_per_grid)-1

        #创建网格
        self.grid_list=GridTraderHttp.create_grid_list(self.ratio_per_grid,self.grid_taker,fund_per_grid,{
            'GridQty':self.grid_gridqty,
            'LowBound':self.grid_lowbound,
            'PriceReserve':self.api_pricereserve,
            'QtyReserve':self.api_qtyreserve})

        self.grid_list.sort(key=lambda x: x['LowPrice'])

        for i in  range(len(self.grid_list)):
            lowprice= self.grid_list[i]['LowPrice']
            upprice= self.grid_list[i]['UpPrice']
            buyqty= self.grid_list[i]['BuyQty']
            sellqty= self.grid_list[i]['SellQty']
            self.log(f'网格编号{i+1} 下沿价格:{lowprice},上沿价格:{upprice},买入手数:{buyqty},卖出手数:{sellqty}')

        ticker={}
        try:
            ticker=self.exchange.fetch_ticker(self.api_symbol)
        except Exception as e:
            strr=str(e)
            retstr= obj_to_json('start',-1,'获取行情失败:{strr}',{})
            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 获取行情失败,{strr}')
            return False,retstr
        
        if self.grid_open> sys.float_info.epsilon:
            if self.grid_open <ticker['last']:
                retstr= obj_to_json('start',-1,'设置的开仓价比最新价小',{})
                return  False,retstr
            last=self.grid_open
        else:
            last=ticker['last']
        
        #根据最新价计算要入场手数
        qty=self.calc_open_qty(last)
        self.log(f'需要买入手数为{qty}')

        #进场
        flag,errmsg=self.open_order(last,qty)
        if flag == False:
            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 建仓失败,{errmsg}')
            retstr= obj_to_json('start',-1,'建仓失败:{errmsg}',{})
            return False,retstr
        
        self.log(f'开仓成功')

        #开启网格挂单
        return self.create_grid(last)

        #开启网格监视器
        # self.order_monitor()

        #self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 网格结束')


    #根据最新价和网格计算出入场时需要买的手数   
    def calc_open_qty(self,last):
        qty=0
        for i in self.grid_list:
            grid=i
            if grid['LowPrice']>last:
                #网格的下沿价格大于当前价,表示此格需要买入
                #需要买入的手数为每格相加
                #需要花费的金额为每格金额相加
                qty=qty+grid['BuyQty']
        return qty
    
   #开启网格
    
    #开仓
    def open_order(self,last,qty):
        #建仓进场
        type=''
        price=0.0
        
        if self.grid_open > sys.float_info.epsilon:
            #有开仓价
            type=self.type[1]
            price=self.grid_open
        else:
            #没有开仓价
            #计算出在滑点范围内的深度
            book=self.exchange.fetch_order_book(self.api_symbol)
            max_price=last*(1+self.grid_slip)
            qty_depth=0
            for price_pair in book['asks']:
                if(price_pair[0]<max_price):
                    qty_depth=qty_depth+price_pair[1]
            
            if qty_depth>qty:
                type=self.type[0]
                price=None
            else:
                type=self.type[1]
                price=last
            

        order,flag,errmsg=self.create_order(type,self.side[0],qty,price)
        if order!=None:
            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 有开仓价{price},开限价进场,委托为:{order}')
            while True:
                order_ret,flag=self.check_order_finish(order['id'])
                if order_ret!=None and flag==True:
                    self.log('市场:'+self.api_exchange+",品种:"+self.api_symbol + ' 建仓成功,建仓手数为:'+str(qty)+',当前价格:'+str(last))
                    return True,None
                else:
                    id=order['id']
                    #self.log(f'开仓单{id}未成交,{order_ret},{flag}')
                    time.sleep(1)
                    continue
        return False,f'开仓失败:{errmsg}'

    #网格挂单
    def create_grid(self,last):
        has_qty=self.has_qty
        for item in self.grid_list:
            qty=0.0
            price=0.0
            side=''
            if last >item['UpPrice']:   #当前价比此网格的上沿价格高,以网格下沿价格挂买单,买入数量为网格买入数
                qty= item['BuyQty']
                price=item['LowPrice']
                side=self.side[0]
            elif last <= item['LowPrice']: #当前价比此网格的下沿价低,以网格的上沿价格挂卖单,卖出数量为网格卖出数
                qty=item['SellQty']
                if(has_qty<qty):
                    qty=has_qty
                has_qty=has_qty-qty
                price=item['UpPrice']
                side=self.side[1]
            else:
                continue

            order,_,errmsg=self.create_order(self.type[1],side,qty,price)
            if order !=None:
                item['Id']=order['id']
                item['Side']=side
                id=order['id']
                self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单成功,委托号为:{id},方向:sell,手数:{qty},价格:{price}')
            else:
                self.stop()
                strr= WebsockerServer.WebsockerServer.obj_to_json('start',-1,f'建仓成功,开启网格失败:{errmsg}',{})
                self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单失败,原因为:{errmsg}')
                return False,strr
        return  True,'ok'

    #定时监控挂单数:
    def order_monitor(self):
        three_hours_num=int((60*60*3)/0.2)
        i=0
        while self.start_flag:
            start= time.time()
            #更新手续费,大概每隔三小时更新一次
            if(i >=three_hours_num):
                i=0
                self.get_account_fee()

            #获取最新价
            last=0.0
            try:
                last=self.exchange.fetch_ticker(self.api_symbol)['last']
            except:
                continue

            #检查挂单
            #print('检查挂单')
            self.update_all_orders2(last)
            i=i+1

            #价格已经到了止损线,止损退出
            if last<self.grid_stop:
                self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 已向下突破止损线,当前价格为{last},止损价格为{self.grid_stop}')
                self.stop_grid()
                break
            
            end=time.time()
            meta_milsec=end-start
            if meta_milsec<=0 or meta_milsec>200:
                time.sleep(0.2)
            else:
                time.sleep(meta_milsec/100)

    def update_all_orders2(self,last):
        try:
            order_list=self.exchange.fetch_open_orders(self.api_symbol)
            
            #获取已成交的委托编号
            open_list=[]
            for item in order_list:
                open_list.append(item['id'])
            orders=[]
            for item in self.grid_list:
                orders.append(item['Id'])
            com_list= list(set(open_list)^ set(orders))

            for item in self.grid_list:
                flag= item['Id'] in com_list
                if flag==True:
                    if len(item['Id']) ==0:
                        qty=0
                        price=0
                        side=''
                        if last >= item['UpPrice']:  #此时最新价大于网格上沿价格,挂买单
                            qty=item['BuyQty']
                            price=item['LowPrice']
                            side=self.side[0]
                        elif last < item['LowPrice']:   #此时最新价小于网格下沿价格,挂卖单
                            qty=item['SellQty']
                            price=item['UpPrice']
                            side=self.side[1]
                        else:
                            continue

                        order,_,errmsg=self.create_order(self.type[1],side,qty,price)
                        if order!=None:
                            item['Id']=order['id']
                            item['Side']=side
                            id=order['id']
                            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单成功,委托号为:{id},方向:{side},手数:{qty},价格:{price}')
                        else:
                            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单失败,原因为:{errmsg}')
                    else:
                        self.add_num(item['Side'])

                        

                        if side== item['Side']: #如果方向相同,表示行情剧烈,在切片检查阶段有行情两次跨过网格线
                            supply_qty=0.0
                            supply_price=0.0
                            supply_side=''
                            if side== self.side[0]:  #两次的行情都是buy,补一个sell
                                supply_qty=item['BuyQty']
                                supply_price=item['UpPrice']
                                supply_side=self.side[1]
                            else:
                                supply_qty=item['SellQty']
                                supply_price=item['LowPrice']
                                supply_side=self.side[0]
                            order1,_,errmsg1=self.create_order(self.type[1],supply_side,supply_qty,supply_price)
                            if order!=None:
                                id=order1['id']
                                self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 补充挂单成功,委托号为:{id},方向:{supply_side},手数:{supply_qty},价格:{supply_price}')
                            else:
                                self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 补充挂单失败,原因为:{errmsg1}')

                        qty=0.0
                        price=0.0
                        side=''
                        if last >= item['UpPrice']:  #此时最新价大于网格上沿价格,挂买单
                            qty=item['BuyQty']
                            price=item['LowPrice']
                            side=self.side[0]
                        elif last < item['LowPrice']:   #此时最新价小于网格下沿价格,挂卖单
                            qty=item['SellQty']
                            price=item['UpPrice']
                            side=self.side[1]

                        order,_,errmsg = self.create_order(self.type[1],side,qty,price)
                        if order != None:
                            item['Id']=order['id']
                            item['Side']=side
                            id=order['id']
                            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单成功,委托号为:{id},方向:{side},手数:{qty},价格:{price}')

                        else:
                            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单失败,原因为:{errmsg}')
        except Exception as e:
            err_msg=self.err_paser(e)
            self.log(f'批量查挂单失败,失败原因:{err_msg}')

    #检查账号所有挂单
    def update_all_orders(self,last):
        try:
            order_list=self.exchange.fetch_open_orders(self.api_symbol)
            for item in self.grid_list:
                if len(item['Id']) ==0: #
                    qty=0
                    price=0
                    side=''
                    if last >= item['UpPrice']:  #此时最新价大于网格上沿价格,挂买单
                        qty=item['BuyQty']
                        price=item['LowPrice']
                        side=self.side[0]
                    elif last < item['LowPrice']:   #此时最新价小于网格下沿价格,挂卖单
                        qty=item['SellQty']
                        price=item['UpPrice']
                        side=self.side[1]

                    order,_,errmsg=self.create_order(self.type[1],side,qty,price)
                    if order!=None:
                        item['Id']=order['id']
                        item['Side']=side
                        id=order['id']
                        self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单成功,委托号为:{id},方向:{side},手数:{qty},价格:{price}')
                    else:
                        self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单失败,原因为:{errmsg}')
                else: #
                    flag=GridTraderNet.check_order_isexist_by_id(order_list,item['Id'])
                    if flag == False:   #挂单不在,需要重新挂单
                        if len(item['Id']) >0:
                            self.add_num(item['Side'])

                        qty=0.0
                        price=0.0
                        side=''
                        if last >= item['UpPrice']:  #此时最新价大于网格上沿价格,挂买单
                            qty=item['BuyQty']
                            price=item['LowPrice']
                            side=self.side[0]
                        elif last < item['LowPrice']:   #此时最新价小于网格下沿价格,挂卖单
                            qty=item['SellQty']
                            price=item['UpPrice']
                            side=self.side[1]

                        order,_,errmsg = self.create_order(self.type[1],side,qty,price)
                        if order != None:
                            item['Id']=order['id']
                            item['Side']=side
                            id=order['id']
                            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单成功,委托号为:{id},方向:{side},手数:{qty},价格:{price}')
                        else:
                            self.log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单失败,原因为:{errmsg}')
                    else: #找到了不做任何操作
                        continue
        except Exception as e:
            err_msg=self.err_paser(e)
            self.log(f'批量查挂单失败,失败原因:{err_msg}')

    def add_num(self,side):
        if side==self.side[0]:
            self.lock.acquire()
            self.buy_num=self.buy_num+1
            self.lock.release()
        else:
            self.lock.acquire()
            self.sell_num=self.sell_num+1
            self.lock.release()

    def query(self):
        buy,sell=0,0
        self.lock.acquire()
        buy,sell=self.buy_num,self.sell_num
        self.lock.release()
        return buy,sell

    #通过id查找挂单
    @staticmethod
    def check_order_isexist_by_id(order_list,id):
        for item in order_list:
            if item['id']==id:
                return True
        return False

    def stop(self):
        self.start_flag=False
        try:
            order_list=self.exchange.fetch_open_orders(symbol=self.api_symbol)
            for item in order_list:
                self.cancel_order(item['id'])
            return True,f'网格关闭'
        finally:
            return True,f'网格关闭'
            
    def create_order(self,type,side,qty,price=None):
        try:
            order = self.exchange.create_order(self.api_symbol,type,side,qty,price)
            return order,True,None
        except Exception as e:
            strmsg=self.err_paser(e)
            self.log(f'创建委托失败,品种:{self.api_symbol},委托类型:{type},方向:{side},价格:{price},手数:{qty},错误:{strmsg}')
            return None,False,strmsg
    
    def cancel_order(self,id):
        try:
            self.exchange.cancel_order(id,self.api_symbol)
            # self.log_order(f'cancel,success,{self.api_symbol},{id}')
        except Exception as e:
            strmsg=self.err_paser(e)
            # self.log_order(f'cancel,fail:{strmsg},{self.api_symbol},{id}')
            self.log(f"撤单失败,订单号:{id},失败原因:{strmsg}")
    
    def check_order_finish(self,id):
        try:
            order=self.exchange.fetch_order(id,self.api_symbol)
            if order==None:
                return None,False
            if order['status']=='closed':
                #记录持有手数
                if order['side'] ==self.side[0]:
                    self.buy_trade(order)
                else:
                    self.sell_trade(order)

                #开单手数减去手续费扣得币
                # qty=float(order['filled'])
                # fee=0
                # if order['fee']!=None and order['fee']['cost']!=None:
                #     fee = float(order['fee']['cost'])
                # side=order['side']
                # price=float(order['price'])
                # currency=''
                # if order['fee']!=None and order['fee']['currency']!=None:
                #     currency=order['fee']['currency']
                # id=order['id']
                # type=order['type']
                # self.log_order(f'closed,success,{self.api_symbol},{id},{type},{side},{price},{qty},{currency},{fee}')
                return order,True
            return order,False
        except Exception as e:
            emsg=self.err_paser(e)
            self.log(f'委托查询错误,错误信息为:{emsg}')
            return None,False

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

    #止损
    def stop_grid(self):
        #将所有挂单清掉
        self.stop()
        # for  _,value in self.order_dict.items():
        #     id=value['id']
        #     self.cancel_order(id)
        #     self.log(f'程序结束,将挂单{id}撤掉')
        # del self.order_dict

    #根据价格查找网格数据
    def get_grid_by_price(self,price):
        for index in range(len(self.grid_list)):
            if self.grid_list[index]['price'] == price:
                return self.grid_list[index]
        return None

    #根据网格设置计算出所有网格的上下沿价格           
    @staticmethod
    def create_grid_list(ratio,taker, fund,data):
        grid_qty=int(data['GridQty'])
        low_bound=float(data['LowBound'])
        price_reserve=int(data['PriceReserve'])
        qty_reserve=int(data['QtyReserve'])

        grid_list=[]
        for i in range(0,grid_qty):
            #此格的下沿价格
            low_price=low_bound*(1+ratio)**(i)
            low_price=GridTraderNet.cut(low_price,price_reserve)
            #此格的上沿价格
            up_price=low_price*(1+ratio)
            up_price=GridTraderNet.cut(up_price,price_reserve)
            #此格买入的手数
            buy_qty=fund/low_price
            buy_qty=GridTraderNet.cut(buy_qty,qty_reserve)
            #此格卖出的手数
            sell_qty=fund/low_price*(1-taker)
            sell_qty=GridTraderNet.cut(sell_qty,qty_reserve)

            grid_list.append(dict([
                ('LowPrice',low_price),
                ('UpPrice',up_price),
                ('BuyQty',buy_qty),
                ('SellQty',sell_qty),
                ('Id',''),
                ('Side','')
                ]))
        return grid_list

    @staticmethod
    def parms_check(jsondata):
        exchange=jsondata['Exchange']
        symbol=jsondata['Symbol']
         #exchange
        if exchange.lower() !='okex' and exchange !='ftx':
            return  False,'交易所设置错误,目前只支持OKEX或者FTX'
        
        #交易品种
        if len(symbol)==0:
            return False,'交易品种不能为空'

        #价格保留数
        price_reserve=int(jsondata['PriceReserve'])
        if price_reserve<0 or price_reserve >8:
            return False,'价格保留位数设置错误,必须大于0小于8'
        
        #手数保留数
        qty_reserve=int(jsondata['QtyReserve'])
        if qty_reserve<0 or qty_reserve>8:
            return False,'手数保留位数设置错误,必须大于0小于8'
            
        #天地格
        up_bound=float(jsondata['UpBound'])
        if up_bound<=0:
            return False,'天格不能小于等于0'

        low_bound=float(jsondata['LowBound'])
        if low_bound <=0:
            return False,'地格不能小于等于0'

        if up_bound <=low_bound:
            return False,'天格价格必须大于地格价格'

        open=float(jsondata['Open'])
        if open >sys.float_info.epsilon:
            if open <low_bound or open > up_bound:
                return False,'开仓价必须大于地格价格小于天格价格'

        #网格数量
        grid_qty=int(jsondata['GridQty'])
        if grid_qty<=0:
            return False,'网格数量不能小于等于0'

        #资金
        ammount=float(jsondata['Ammount'])
        if ammount<=0:
            return False,'资金数据不能小于等于0'

        #止损价
        # stop=float(jsondata['Stop'])
        # if stop<=0 or stop >=low_bound:
        #     return False,'止损价不能大于地格或小于等于0'

        #滑点
        slip=float(jsondata['Slip'])
        if slip <0:
            return False,'滑点不能小于等于0'
        
        return True,'OK'
        

    def read_config_by_obj(self,jsondata):
        #print(str(jsondata))
        flag,msg=GridTraderHttp.parms_check(jsondata)
        if flag==False:
            return False,msg

        exchange=jsondata['Exchange']
        symbol=jsondata['Symbol']

        #exchange
        self.api_exchange=exchange

        #交易品种
        self.api_symbol=symbol

        logname=exchange+symbol+'.log'
        self.gl_logfile=logname
        orderfile=exchange+symbol+'.csv'
        self.gl_orderfile=orderfile

        #apikey
        self.api_apikey=jsondata['ApiKey']

        #secret
        self.api_secret=jsondata['Secret']

        #密码
        self.api_passwd=jsondata['Password']

        #价格保留数
        self.api_pricereserve=int(jsondata['PriceReserve'])

        #手数保留数
        self.api_qtyreserve=int(jsondata['QtyReserve'])

        #天地格
        self.grid_upbound=float(jsondata['UpBound'])
        self.grid_lowbound=float(jsondata['LowBound'])

        self.grid_open=float(jsondata['Open'])

        #网格数量
        self.grid_gridqty=int(jsondata['GridQty'])

        #资金
        self.grid_ammount=float(jsondata['Ammount'])

        #止损价
        self.grid_stop=float(jsondata['Stop'])

        #滑点
        self.grid_slip=float(jsondata['Slip'])

        return True,'ok'

    def log(self,msg,withTime=True):
        timestamp=datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%b %d %Y %H:%M:%S.%f, ")
        try:
            f=open(f"log.log",'a')
            if withTime:
                f.write(timestamp+msg+"\n")
            else:
                f.write(msg+"\n")
            f.close()
        except:
            pass

    def err_paser(self,e):
        if self.api_exchange==self.exchange_list[0]:
            return GridTraderHttp.okex_err_paser(e)
        elif self.api_exchange==self.exchange_list[1]:
            return GridTraderHttp.ftx_err_paser(e)
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
    grid_trader=GridTraderHttp()
    if grid_trader.init() == True:
        grid_trader.grid_start()
