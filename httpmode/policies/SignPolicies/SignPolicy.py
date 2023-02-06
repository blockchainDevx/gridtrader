from policies.CommonGridTrader import *
from trdapiwrap.TraderAPI import TraderAPI
from common.common import *
from .MasterCoin import IsMasterCoin
from .CalcFixedTP import CalcFixedTP
from .SignPolicyQuoteMgr import SPQuoteMgr
from .FixedTPObj import FixedTPTask
from .FloatingTPObj import FloatingTPTask
from policies.SignPolicies import TradeBYAmmountNormal,TradeBYAmmountGate,TradeBYAmmountOK

#交易类型默认为全买
def SelTradeHD(exname):
    trade_cb=TradeBYAmmountNormal.trade_by_ammount_normal
    if exname  == OKEX:
        trade_cb=TradeBYAmmountOK.trade_by_ammount_ok
    elif exname == GATE:
        trade_cb=TradeBYAmmountGate.trade_by_ammount_gate
    return trade_cb

class SignPolicy(IGridTrader):
    def __init__(self):
        self._apis=[]
        self._con_data={
            'AmmountType':'',
            'Symbol':'',
            'PMin':1,
            'PDigit':2,
            'QMin':1,
            'QDigit':2,
            'StopPercent':0,
            'LastSide':SELL,  #对象初始化时上次的买卖信号设置为卖
            'IsMasterCoin':False  #是否为主流币
        }
        self._keyname=''
        self._signtype=''
        self._trade_cb=None       #交易的函数
        self._tp_data={
            'TPMode':TP_NONE,   #止盈的模式 ,0:没有止盈,1:固定止盈,2:浮动止盈
            'TPFLTMode': TP_FLT_PER,    #浮动止盈的计算类型,0:按价格百分比计算,1:按价格与配置值相减计算
            'TPFLTPoint':0.0
        }
        self._is_master=False   #是否是主流币

    def init(self,params):
        if 'symbol' not in params or \
            'keyName' not in params or \
            'qmin' not in params or \
            'qdigit' not in params or\
            'signType' not in params or \
            'tpMode' not in params:
                return False
            
        #保存下单函数
        
        #保存止盈数据,止盈模式和止盈点计算函数
        self._tp_data['TPMode']=params['tpMode']
        
        #保存策略配置信息
        self._con_data['Symbol']=params['symbol']
        if 'qty' in params:
            self._con_data['Qty']=int(params['qty'])
        self._keyname=params['keyName']
        self._signtype=params['signType']
        self._con_data['QMin']=params['qmin']
        self._con_data['QDigit']=params['QDigit']
        
        
        #止损配置
        if 'stopPer' in params and 'qmin' in params and 'qdigit' in params:
            self._con_data['StopPercent']=params['stopPer']
            self._con_data['PMin']=self._con_data['QMin']
            self._con_data['PDigit']=self._con_data['QDigit']
            
        #止盈配置
        if 'fltMode' in params and 'fltPoint' in params:
            if params['fltMode']== TP_FLT_PER and float(params['fltPoint']) > 1.0:
                return False
            self._tp_data['TPFLTMode'] = params['fltMode']
            self._tp_data['TPFLTPoint'] = float(params['fltPoint'])
            
        symbollist=self._con_data['Symbol'].split('/')
        if len(symbollist)==2:
            self._cointype=symbollist[0]
            self._con_data['AmmountType']=symbollist[1]
        else:
            self._cointype=''
            self._con_data['AmmountType']=''
            
        #判断是否为主流币
        self._is_master= IsMasterCoin(self._con_data['Symbol'])
        return True
        
    #网格开始
    def start(self,apilist):
        for item in apilist:
            groupname=item['GroupName']
            tradefunc=SelTradeHD(item['Exchange'])
            tradehd=TraderAPI(groupname)
            tradehd.CreateExHandler(item['Exchange'],item['Content'])
            _,taker=tradehd.FetchTradingFee(self._con_data['Symbol'])
            self._apis.append({ 
                'TraderName': '{0}|{1}'.format(self._keyname, item['GroupName']),
                'TraderHD':tradehd,
                'Taker':taker,
                'TraderFunc':tradefunc})

            RecordData('=====网页 {0} 启动,账号: {1} ,品种为: {2} ,信号类别为: {3} ======'.format(
                self._keyname,
                groupname,
                self._con_data['Symbol'],
                self._signtype
            ))
        pass
 
    #开启监视器
    def create_order(self,side, price=0):
        RecordData(f'---------网页 {self._keyname} 触发信号---------')
        RecordData('信号触发:方向为: {0} ,品种: {1} ,信号类别为: {2}'.format(side,self._con_data['Symbol'],self._signtype))
        for item in self._apis:
            qty,price=item['TraderFunc'](side,item,self._con_data)
            
            #有止盈的执行止盈
            if side==BUY and qty!=None and price !=None: 
                if self._tp_data['TPMode'] == TP_FIXED: #固定止盈
                    #根据账号的手续费率计算出买入扣费之后所得的币数量
                    qty_m=Func_DecimalCut2(qty*(1-item['Taker']),self._con_data['QDigit'],self._con_data['QMin'])   
                    tp_data=CalcFixedTP(qty_m,price,
                                        self._con_data['QMin'],self._con_data['QDigit'],
                                        self._con_data['PMin'],self._con_data['PDigit'],
                                        self._is_master)
                    #开启定时任务,检测止盈
                    if len(tp_data) >0:
                        SPQuoteMgr().addtask(FixedTPTask(item,self._con_data,tp_data))
                        msg='开启止盈,止盈模式为固定止盈,'
                        for index in range(0,len(tp_data)):
                            msg=msg+'止盈点 {0},币数为 {1},价格为 {2}'.format(index,tp_data[index][0],tp_data[index][1])
                        RecordData(msg)
                elif self._tp_data['TPMode'] ==  TP_FLOATING:
                    #根据账号的手续费率计算出买入扣费之后所得的币数量
                    qty_m=Func_DecimalCut2(qty*(1-item['Taker']),self._con_data['QDigit'],self._con_data['QMin'])   
                    # qty_m=qty*(1-item['Taker'])
                    SPQuoteMgr().addtask(FloatingTPTask(item, 
                                                        self._con_data,
                                                        self._tp_data,
                                                        qty_m,
                                                        price))
                    pass
        pass
        RecordData(f'------------------------------------')
            
    #关闭网格
    def stop(self):
        pass
    

    