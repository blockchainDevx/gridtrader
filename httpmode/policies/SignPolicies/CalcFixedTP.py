from common.common import Func_DecimalCut2

__all__=['CalcFixedTP']

''' 主流币的 固定止盈 指标
    涨 5% 止盈 5%,
      10%     20%,
      15%     30%,
      20%     30%,
      30%     15%
'''
MasterQuote=[
    (0.05, 0.05),
    (0.1,  0.2),
    (0.15, 0.3),
    (0.2,  0.3),
    (0.3,  0.15)
]

''' 山寨币的 固定止盈 指标
    涨 10% 止盈   5%,
       20%      20%,
       30%      30%,
       40%      30%,
       50%      15%
'''
CopycatQuote=[
    (0.1,  0.05),
    (0.2,  0.2),
    (0.3,  0.3),
    (0.4,  0.3),
    (0.5,  0.15)
]

def CalcFixedTP(qty,price,qmin,qdigit,pmin,pdigit,is_master=False):
    return _calfixedtp(qty,price,qmin,qdigit,pmin,pdigit,MasterQuote if is_master else CopycatQuote)
  
def _calfixedtp(qty,price,qmin,qdigit,pmin,pdigit,quotes):
    qty_tol=0.0
    lis=[]
    for item in quotes:
        qty_m=Func_DecimalCut2(qty*(item[1]),qdigit,qmin)
        if qty_m <=0.0:
            continue
        price_m=Func_DecimalCut2(price*(1+item[0]),pdigit,pmin)
        qty_remaining=qty-qty_tol
        lis.append((qty_m if qty_remaining > qty_m else qty_remaining,price_m))
        qty_tol=qty_tol+qty_m
    return lis