from pickle import MARK
from CommonGridTrader import *
import sys
import time

from TraderAPI import TraderAPI
from Logger import Logger

'''
数据结构:
{
    GridType:网格类型,
    Exchange:交易所,
    Symbol:品种,
    PriceRes:价格精度,
    QtyRes:手数精度,
    Open:开仓价,
    RisRatio:上升比例,
    RetRatio:回撤比例,
    UpBound:天格价格,
    GridQty:网格数,
    Amount:金额,
    Ratio:滑点,
    GroupId:API选择
}
'''

class HalfGridTrader(IGridTrader):
    def __init__(self):
        super().__init__()
        self.grid_maker=0.0
        self.grid_taker=0.0
        self.trade_hd=TraderAPI()
        self.start_flag=False
        self.grid_risratio=0.0
        self.grid_retratio=0.0
        self.api_subaccount=''
        pass
    
    #参数检查
    @staticmethod
    def parms_check(json_data):
        exchange=json_data.get('Exchange')
        if exchange == None or len(exchange)==0:
            return False,'缺少交易所名称'
        
        if exchange.lower() != 'okex' and exchange.lower() != 'ftx' and exchange.lower() !='binance':
            return False,'交易所设置错误,目前只支持OKEX,FTX或BINANCE'
        
        symbol=json_data.get('Symbol')
        if symbol==None or len(symbol)==0:
            return False,'交易所品种必须要设置'
        
        price_res=json_data.get('PriceReserve')
        if price_res == None or int(price_res)<0 or int(price_res)>8:
            return False,'价格保留位数设置错误,必须大于0小于8'

        up_bound=json_data.get('UpBound')
        if up_bound ==None or float(up_bound) < sys.float_info.epsilon:
            return False,'天格不能小于等于0'
        
        open=json_data.get('Open')
        if open==None :
            return False,'1开仓价必须小于天格价格大于或等于0'
        open=float(open)
        if open<0:
            return False,'2开仓价必须小于天格价格大于或等于0'
        
        if open > float(up_bound):
            return False,'3开仓价必须小于天格价格大于或等于0'

        ris_ratio=json_data.get('RisRatio')
        if ris_ratio==None or float(ris_ratio) < sys.float_info.epsilon:
            return False,'上升比例必须大于0'

        ret_ratio=json_data.get('RetRatio')
        if ret_ratio==None or float(ret_ratio) < sys.float_info.epsilon:
            return False,'回撤比例必须大于0'

        grid_qty=json_data.get('GridQty')
        if grid_qty == None or int(grid_qty) <=0:
            return False,'网格数量不能小于等于0'
        
        amount=json_data.get('Amount')
        if amount==None or float(amount) <=sys.float_info.epsilon:
            return False,'资金数据不能小于等于0'
        
        slip=json_data.get('Slip')
        if slip == None or float(slip) < sys.float_info.epsilon:
            return False,'滑点不能小于0'
        
        return True,'OK'

    #网格计算
    @staticmethod
    def grid_calc(api,data):
        #创建交易所对象
        ex_name=data['Exchange']
        trader=TraderAPI()
        flag=trader.CreateExHandler(ex_name,api)
        if flag==False:
            return False,f'交易所{ex_name}不支持'
        
        symbol=data['Symbol']
                         
        #账号费率
        grid_maker=0.0
        grid_taker=0.0
        if ex_name!=FTX:
            grid_maker,grid_taker=trader.FetchTradingFee(symbol)
        
        up_bound=float(data['UpBound'])
        grid_qty=int(data['GridQty'])
        amount=float(data['Amount'])
        price_res=int(data['PriceReserve'])
        qty_res=int(data['QtyReserve'])
        lower=0.0
        open=float(data['Open'])
        ticker=None
        timestamp=0

        #如果开仓价为0,那么最新价为最低价
        if open<sys.float_info.epsilon:
            ticker=trader.FetchTicker(symbol)
            if ticker==None:
                return False,'获取最新价格失败',None
            
            lower=ticker['last']
            timestamp=ticker['timestamp']
        else:
            timestamp=int(round(time.time()*1000))
            lower=open
        
        ratio_per_grid=(up_bound/lower)**(1/grid_qty)-1
        fund_per_grid=amount/grid_qty

        net_profit=((1-grid_maker)**2)*(1+ratio_per_grid)-1

        #创建网格数组
        grid_list=Func_CreateGrid({
            'Ratio':ratio_per_grid,
            'Taker':grid_taker,
            'Fund':fund_per_grid,
            'Qty':grid_qty,
            'Lower':lower,
            'PriceRes':price_res,
            'QtyRes':qty_res
        })
        if grid_list==None or len(grid_list)==0:
            return False,'创建网格失败',None

        #计算出需要
        qty=0
        cost_ammount=0
        for i in grid_list:
            grid=i
            if grid['LowPrice']>lower:
                #网格的下沿价格大于当前价,表示此格需要买入
                #需要买入的手数为每格相加
                #需要花费的金额为每格金额相加
                qty=qty+grid['BuyQty']
                cost_ammount=cost_ammount+fund_per_grid
        
        #剩余的金额=总金额-花费的金额
        remaining=amount-cost_ammount

        #扣除手续费之后的净手数=手数*(1-市价手续费)
        net_qty=qty*(1-grid_taker)

        return True,'OK',dict([
            ('Time',timestamp),
            ('RatioPerGrid',ratio_per_grid),
            ('FundPerGrid',fund_per_grid),
            ('ProFitPerGrid',ratio_per_grid),
            ('NetProfitPerGrid',net_profit),
            ('LastPrice',lower),
            ('EntryQty',qty),
            ('NetEntryQty',net_qty),
            ('AmountSpent',cost_ammount),
            ('RemainingAmount',remaining)
            ])

        pass

    #读取配置
    def read_config_by_obj(self,api,json_data):
        #入参数据检查
        flag,msg=HalfGridTrader.parms_check(json_data)
        if flag==False:
            return False,msg
        
        #exchange
        self.api_exchange=json_data['Exchange']

        #symbol
        self.api_symbol=json_data['Symbol']

        #coin
        symbollist=self.api_symbol.split('/')
        if len(symbollist)>1:
            self.coin=symbollist[0]
            self.coinpair=symbollist[1]

        #apikey
        self.api_apikey=api['API']['ApiKey']

        #secret
        self.api_secret=api['API']['Secret']

        #密码
        self.api_passwd=api['API']['Password']

        #subaccount
        subaccount=api.get('Subaccount')
        if subaccount!=None and len(subaccount)!=0:
            self.api_subaccount=subaccount

        #价格保留数
        self.api_pricereserve=int(json_data['PriceReserve'])

        #手数保留数
        self.api_qtyreserve=int(json_data['QtyReserve'])

        #天格
        self.grid_upbound=float(json_data['UpBound'])

        #上升比例
        self.grid_risratio=float(json_data['RisRatio'])

        #回撤比例
        self.grid_retratio=float(json_data['RetRatio'])

        #开仓价
        self.grid_open=float(json_data['Open'])

        #网格数量
        self.grid_gridqty=int(json_data['GridQty'])

        #资金
        self.grid_ammount=float(json_data['Amount'])

        #止损价
        self.grid_stop=float(json_data['Stop'])

        #滑点
        self.grid_slip=float(json_data['Slip'])

        return True,'ok'
        pass

    #网格开始
    def start(self,factor=0):
        #创建交易所句柄
        self.trade_hd.CreateExHandler(self.api_exchange,{
            'API':{
                'ApiKey':self.api_apikey,
                'Secret':self.api_secret,
                'Password':self.api_passwd
            },
            'Subaccount':self.api_subaccount
        })

        #获取账号手续费率
        if self.api_exchange!=FTX:
            self.grid_maker,self.grid_taker=self.trade_hd.FetchTradingFee(self.api_symbol)
        
        #获取账号资金
        balance=self.trade_hd.FetchBalance()
        if balance ==None:
            return False,f'获取账号余额失败',None

        #账号已有的币数量
        symbol_qty=balance['total'][f'{self.coin}']

        #账号的基币数量
        coin_amount=balance['total'][f'{self.coinpair}']

        #基币数量与网格配置比较
        if coin_amount < self.grid_ammount:
            return False,f'账户余额比网格设置金额要小,币种{self.coin},账号余额{coin_amount}',None

        #获取市场最新价
        ticker=self.trade_hd.FetchTicker(self.api_symbol)
        if ticker == None:
            return False,'获取最新行情失败',None
        
        #获取网格的地格价格
        grid_lowbound=float(ticker['last'])
        if self.grid_open > sys.float_info.epsilon:
            if self.grid_open>grid_lowbound:
                return False,f'开仓价{self.grid_open}大于市场最新价{grid_lowbound}',None
            else:
                grid_lowbound=self.grid_open

        #将上升比例的价格计算出
        self.grid_risbound=grid_lowbound*(1+self.grid_risratio)
        #初始化时回撤价格与上升比例价格一致
        self.grid_retbound=self.grid_risbound

        if grid_lowbound==0.0:
            return False,f'获取最新价格失败',None

        #每格利润
        ratio_per_grid=(self.grid_upbound/grid_lowbound)**(1/self.grid_gridqty)-1

        #计算出每格资金,
        fund_per_grid=self.grid_ammount/self.grid_gridqty
        fund_per_grid=Func_DecimalCut(fund_per_grid,self.api_pricereserve)

        #计算出每格的纯利润,数据不变
        #net_profit=((1+self.grid_maker)**2)*(1+ratio_per_grid)-1

        #建立网格数组
        self.grid_list=Func_CreateGrid({
            'Ratio':ratio_per_grid,
            'Taker':self.grid_taker,
            'Fund':fund_per_grid,
            'Qty':self.grid_gridqty,
            'Lower':grid_lowbound,
            'PriceRes':self.api_pricereserve,
            'QtyRes':self.api_qtyreserve
        })
        self.grid_list.sort(key=lambda x:x['LowPrice'])

        #计算出需要进场的手数
        qty=HalfGridTrader.calc_open_qty(grid_lowbound,self.grid_list)
        Logger().log(f'需要进场的手数为{qty}')

        #账号已有的币的手数 比需要进场的币的手数多
        if symbol_qty >qty:
            self.has_qty=qty
            return True,'OK',None
        else:
            #剩下手数开仓
            err_msg,id=self.open_order(grid_lowbound,qty-symbol_qty)
            if id==None:
                return False,'建仓失败',None
            return True,'OK',id
        pass

    #开启监视器
    def create_monitor(self,orderid,lock):
        self.thread=threading.Thread(target=self.order_monitor,args=(orderid,lock,))
        self.thread.start()
        pass

    #关闭网格
    def stop(self):
        self.start_flag=False
        order_list=self.trade_hd.FetchOpenOrders(self.api_symbol)
        if order_list!=None:
            for item in order_list:
                self.trade_hd.CancelOrder(item['id'])
            
        balance=self.trade_hd.FetchBalance()
        if balance!=None:
            qty=balance['total'][f'{self.coin}']
            if qty> sys.float_info.epsilon:
                self.trade_hd.CreateOrder(self.api_symbol,MARKET,SELL,qty)
        Logger().log('网格关闭,所有挂单撤销,所有持仓清仓')
        return True,'网格关闭'
        pass

    #开仓
    def open_order(self,last,qty):
        #建仓进场
        type=''
        price=0.0
        
        if self.grid_open > sys.float_info.epsilon:
            #有开仓价
            type=LIMIT
            price=self.grid_open
        else:
            #没有开仓价
            #计算出在滑点范围内的深度
            book=self.trade_hd.FetchOrderBook(self.api_symbol)
            if book== None:
                return f'获取行情深度失败',None

            max_price=last*(1+self.grid_slip)
            qty_depth=0
            for price_pair in book['asks']:
                if(price_pair[0]<max_price):
                    qty_depth=qty_depth+price_pair[1]
            
            if qty_depth>qty:
                type=MARKET
                price=None
            else:
                type=LIMIT
                price=last

        order=self.trade_hd.CreateOrder(self.api_symbol, type,BUY,qty,price)
        if order==None:
            return f'开仓失败',None
        return 'OK',order['id']

    @staticmethod
    def calc_open_qty(last,grid_list):
        qty=0
        for i in grid_list:
            grid=i
            if grid['LowPrice']>last:
                #网格的下沿价格大于当前价,表示此格需要买入
                #需要买入的手数为每格相加
                #需要花费的金额为每格金额相加
                qty=qty+grid['BuyQty']
        return qty

    def order_monitor(self,id,lock=None):
        print('网格监视器开启')
        #直到建仓的委托完全成交
        if id != None:
            while True:
                order=self.trade_hd.FetchOrder(id,self.api_symbol)
                if order!=None and order['status']=='closed':
                    if order['side']==BUY:
                        self.buy_trade(order)
                    else:
                        self.sell_trade(order)
                    break
                else:
                    time.sleep(1)
                    continue 

        #建立网格
        ticker=self.trade_hd.FetchTicker(self.api_symbol)
        if ticker==None:
            Logger().log('网格开启错误,获取最新行情失败')
            return 
        
        if lock!=None:
            lock.acquire()
        flag=self.create_grid(ticker['last'])
        if lock!=None:
            lock.release()
        if flag==False:
            Logger().log('网格开启错误,网格建立失败')
            return 

        self.start_flag=True
        three_hours_num=int((60*60*3)/0.2)
        i=0
        while self.start_flag:
            start= time.time()
            #更新手续费,大概每隔三小时更新一次
            # if(i >=three_hours_num):
            #     i=0
            #     self.get_account_fee()

            #更新网格
            self.update_grid()

            #检查挂单
            self.update_all_order()
            i=i+1

            #价格已经到了止损线,止损退出
            if self.is_stop() == True:
                break
            
            end=time.time()
            meta_milsec=end-start
            if meta_milsec < 0.2:
                time.sleep(0.2-meta_milsec)
        pass

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
        Logger().log(f'网格挂单成交,委托号为:{id},方向为:买,成交手数为:{fill},委托价格为:{price}')

        pass

    def sell_trade(self,info):
        fill=info['filled']
        price=info['price']
        self.has_qty=self.has_qty-fill
        id=info['id']
        Logger().log(f'网格挂单成交,委托号为:{id},方向为:卖,成交手数为:{fill},委托价格为:{price}')

    def create_grid(self,last):
        has_qty=self.has_qty
        for item in self.grid_list:
            start=time.time()
            qty=0.0
            price=0.0
            side=''
            if last >item['UpPrice']:   #当前价比此网格的上沿价格高,以网格下沿价格挂买单,买入数量为网格买入数
                qty= item['BuyQty']
                price=item['LowPrice']
                side=BUY
            elif last <= item['LowPrice']: #当前价比此网格的下沿价低,以网格的上沿价格挂卖单,卖出数量为网格卖出数
                qty=item['SellQty']
                if(has_qty<qty):
                    qty=has_qty
                has_qty=has_qty-qty
                qty=Func_DecimalCut(qty,self.api_qtyreserve)
                price=item['UpPrice']
                side=SELL
            else:
                continue

            order=self.condition_create_order(self.api_symbol,LIMIT,side,qty,price,last)
            end=time.time()
            meta_time=end-start
            if meta_time<0.2:
                time.sleep(0.2-meta_time)
            if order !=None:
                item['Id']=order['id']
                item['Side']=side
                id=order['id']
                Logger().log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单成功,委托号为:{id},方向:sell,手数:{qty},价格:{price}')
            else:
                self.stop()
                Logger().log(f'建仓成功,开启网格失败')
                return False
        return True

    def update_grid(self):
        ticker= self.trade_hd.FetchTicker(self.api_symbol)
        if ticker==None:
            return
        
        last=ticker['last']
        if last <= sys.float_info.epsilon:
            return
        
        #算出当前回撤点
        lower=self.grid_retbound*(1+self.grid_retratio)
        if last >= lower:   #最新价比回撤点要高
            #更新回撤价格
            self.grid_retbound=lower
            for item in self.grid_list[:]:
                if item['UpPrice'] <lower: 
                    #网格的上沿价格小于最新价,将该网格挂单撤掉并删除该网格
                    #撤单
                    self.trade_hd.CancelOrder(item['Id'])
                    #删除网格
                    self.grid_list.remove(item)
                elif item['UpPrice']>lower and item['LowPrice'] <lower: 
                    #网格上沿价格大于最新价且网格下沿价格小于最新价,将网格下沿价格改为最新价,并且如果该网格挂单为买,撤单再按最新价买入
                    #修改网格下沿价格
                    item['LowPrice']=lower
                    if item['Side']==BUY:
                        #撤单
                        self.trade_hd.CancelOrder(item['Id'])
        pass
    
    def update_all_order(self):
        order_list=self.trade_hd.FetchOpenOrders(self.api_symbol)
        if order_list==None:
            return
        
        ticker=self.trade_hd.FetchTicker(self.api_symbol)
        if ticker== None:
            return

        last=float(ticker['last'])
        if last <=sys.float_info.epsilon:
            return

        open_list=[]
        for item in order_list:
            open_list.append(item['id'])
        orders=[]
        for item in self.grid_list:
            orders.append(item['Id'])
        com_list= list(set(open_list)^ set(orders))

        #遍历网格委托,
        for item in self.grid_list:
            #检查网格委托是否在未完成列表中
            flag=item['Id'] in com_list
            if flag==True:
                #根据价格来判断新补的仓位是买还是卖
                    qty=0
                    price=0
                    side=''
                    if last >= item['UpPrice']:  #此时最新价大于网格上沿价格,挂买单
                        qty=item['BuyQty']
                        price=item['LowPrice']
                        side=BUY
                    elif last < item['LowPrice']:   #此时最新价小于网格下沿价格,挂卖单
                        qty=item['SellQty']
                        price=item['UpPrice']
                        side=SELL
                    else:
                        continue

                    if len(item['Id']) ==0:
                        order=self.condition_create_order(self.api_symbol, LIMIT,side,qty,price,last)
                        if order!=None:
                            item['Id']=order['id']
                            item['Side']=side
                            id=order['id']
                            Logger().log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单成功,委托号为:{id},方向:{side},手数:{qty},价格:{price}')
                    else:
                        #补漏掉触发的委托
                        self.cover_order(side,item,last)

                        #补缺口委托
                        # self.add_num(item['Side'])  
                        order = self.condition_create_order(self.api_symbol,LIMIT,side,qty,price,last)
                        if  order != None:
                            item['Id']=order['id']
                            item['Side']=side
                            id=order['id']
                            Logger().log(f'市场:{self.api_exchange},品种{self.api_symbol} 挂单成功,委托号为:{id},方向:{side},手数:{qty},价格:{price}')

    def cover_order(self,side,item,last):
        if side== item['Side']: #如果方向相同,表示行情剧烈,在切片检查阶段有行情两次跨过网格线
            supply_qty=0.0
            supply_price=0.0
            supply_side=''
            if side== BUY:  #两次的行情都是buy,补一个sell
                supply_qty=item['BuyQty']
                supply_price=item['UpPrice']
                supply_side=SELL
            else:
                supply_qty=item['SellQty']
                supply_price=item['LowPrice']
                supply_side=BUY
            order=self.condition_create_order(self.api_symbol,LIMIT,supply_side,supply_qty,supply_price,last)
            if order!=None:
                id=order['id']
                Logger().log(f'市场:{self.api_exchange},品种{self.api_symbol} 补充挂单成功,委托号为:{id},方向:{supply_side},手数:{supply_qty},价格:{supply_price}')

    def condition_create_order(self,symbol,type,side,qty,price,last):
        #超过上升价格就不买了
        if side==BUY and last >self.grid_risbound:
            return None

        order=self.trade_hd.CreateOrder(symbol,type,side,qty,price)
        return order
        pass

    def is_stop(self):
        ticker=self.trade_hd.FetchTicker(self.api_symbol)
        if ticker==None:
            return False
        last=ticker['last']

        #最新价出错
        if last <=sys.float_info.epsilon:
            return False

        #最新价大于上升价格小于回撤价格就完全退出
        if last > self.grid_risbound and last < self.grid_retbound :
            Logger().log(f'价格{last}已跌到回撤价格{self.grid_retbound}以下')
            self.stop()
            return True
        return False