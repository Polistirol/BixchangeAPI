from django.dispatch.dispatcher import receiver
from app import services_app as svc
from .msg_manager import msg 
from app import models 


def market_order_pool(newOrder,openOrders) :
    '''
Outputs a list of all the orders needed to fulfill a market order, 
As well as the total amount of usd necessary to cover them all.
'''
    marketBuyPool=[]
    amountToCover=newOrder.amount
    usdNeeded= 0
    if newOrder.type in [1,3,5]:
        openOrders= openOrders.order_by("USDprice","-type","datetime")
    elif newOrder.type in [2,4,6]:
        openOrders= openOrders.order_by("-USDprice","-type","datetime")
    for order in openOrders:
        if amountToCover >0:
            #full orders
            if order.type == 6 or order.type == 5 : 
                if order.amount > amountToCover: #sells more that order can buy
                    continue
                else :
                    amountToCover -= order.amount #amount left is decreased, full order is added to pool
                    usdNeeded += order.amount * order.USDprice
                    marketBuyPool.append(order)
            #fast orders
            elif order.type == 4 or order.type == 3 :
                if order.amount >= amountToCover: # order can be fully covered added, and cycle can stop
                    usdNeeded += amountToCover * order.USDprice
                    amountToCover =0
                    marketBuyPool.append(order)
                else: # order is greater than offer , amountToCover is reduced, offer will be closed
                    amountToCover -= order.amount
                    usdNeeded += order.amount * order.USDprice
                    marketBuyPool.append(order)
    if len(marketBuyPool) ==0 or amountToCover >0:
        # if cycle is over and the pool is empty or amountToCover is >0 , than there is not enough liquidity, 
        return None,None
    return marketBuyPool,usdNeeded
    

def unpack_market_pool(newOrder,pool):
    '''takes a list of orders (market pool) and resolves all the matching. 
        If the case, will place a new order.'''
    for order in pool:
        svc.fulfill_order(newOrder,order)
    return

