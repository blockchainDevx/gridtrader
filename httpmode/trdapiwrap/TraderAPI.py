import ccxt
from policies.CommonGridTrader import *
import json
from common.logger.Logger import Logger
from common.common import *

class TraderAPI():
    def __init__(self,name=''):
        self.group_name=name
        self.ex_handler={}
        self.ex_name=''
    #创建交易所句柄
    def CreateExHandler(self,ex,api):
        apidata=api['API']
        if ex==OKEX:
            self.ex_handler=ccxt.okex({
                'enableRateLimit': True,
                'apiKey': apidata['ApiKey'],
                'secret':apidata['Secret'],
                'password':apidata['Password'],
            })
        elif ex ==FTX:
            subaccount=api.get('Subaccount')
            if subaccount == None or len(subaccount)==0:
                self.ex_handler=ccxt.ftx({
                    'enableRateLimit': True,
                    'apiKey': apidata['ApiKey'],
                    'secret':apidata['Secret'],
                })
            else:
                self.ex_handler=ccxt.ftx({
                    'enableRateLimit': True,
                    'apiKey': apidata['ApiKey'],
                    'secret':apidata['Secret'],
                    'headers': {
                        'FTX-SUBACCOUNT': subaccount,
                    },
                })
        elif ex==BINANCE:
            self.ex_handler=ccxt.binance({
                'enableRateLimit': True,
                'apiKey': apidata['ApiKey'],
                'secret':apidata['Secret'],
            })
        elif ex==GATE:
            self.ex_handler=ccxt.gateio({
                'enableRateLimit': True,
                'apiKey': apidata['ApiKey'],
                'secret':apidata['Secret'],
                'options': {
                    'defaultType': 'spot',
                },
            })
        else:
            Logger().log(f'配置的交易所{ex}不支持')
            return False
        self.ex_name=ex
        return True

    #查询账号指定品种的费率
    def FetchTradingFee(self,symbol):
        try:
            fee=self.ex_handler.fetch_trading_fee(symbol)
            if(self.ex_name==FTX):
                return 0.0,0.0
            return abs(fee['maker']),abs(fee['taker'])
        except Exception as e:
            strr=str(e)
            Logger().log(f'交易所连接失败:{strr}')
            return 0.0,0.0

    #查询最新价
    def FetchTicker(self,symbol):
        try:
            ticker=self.ex_handler.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            strr=str(e)
            Logger().log(f'获取最新价格失败:{strr}')
            return None
    
    #查询账号资金
    def FetchBalance(self):
        
        try:
            balance=self.ex_handler.fetch_balance()
            # print(json.dumps(balance))
            return balance
        except Exception as e:
            strr=str(e)
            print(strr)
            Logger().log(f'查询账号资金失败:{strr}')
            return None

    def CreateOrder(self,symbol,type,side,qty,price=None,parms={}):
        try:
            order=self.ex_handler.create_order(symbol,type,side,qty,price,parms)
            return order,None
        except Exception as e:
            err_msg=self.err_parser(e)
            # Logger().log(f'创建委托,品种:{symbol},市场类型:{type},方向:{side},数量:{qty},价格:{price},失败{err_msg}')
            return None,err_msg

    def FetchOrderBook(self,symbol):
        try:
            book=self.ex_handler.fetch_order_book(symbol)
            return book
        except Exception as e:
            err_msg=self.err_parser(e)
            Logger().log(f'查询行情深度失败:{err_msg}')
            return None
        pass
    
    def FetchOpenOrders(self,symbol):
        try:
            order_list=self.ex_handler.fetch_open_orders(symbol)
            return order_list
        except Exception as e:
            err_msg=self.err_parser(e)
            Logger().log(f'查询未完成委托失败:{err_msg}')
            return None
        pass

    def FetchOrder(self,id,symbol=None):
        try:
            order=self.ex_handler.fetch_order(id,symbol)
            return order
        except Exception as e:
            err_msg=self.err_parser(e)
            Logger().log(f'查询委托失败:{err_msg}')
            return None
        pass

    def CancelOrder(self,id):
        try:
            self.ex_handler.cancel_order(id)
        except Exception as e:
            err_msg=self.err_parser(e)
            Logger().log(f'撤单失败:{err_msg}')

    def err_parser(self,e):
        if self.ex_name==OKEX:
            return TraderAPI.OKEX_err_parser(e)
        elif self.ex_name==FTX:
            return TraderAPI.FTX_err_parser(e)
        else:
            return str(e)

    @staticmethod
    def FTX_err_parser(e):
        strr=str(e)
        strr1=strr[strr.find('{'):]
        try:
            str_json=json.loads(strr1)
            return str_json['error']
        except:
            return strr
    
    @staticmethod
    def OKEX_err_parser(e):
        strr=str(e)
        strr1=strr[strr.find('{'):]
        try:
            json_data=json.loads(strr1)
            return json_data['data'][0]['sMsg']
        except:
            return strr