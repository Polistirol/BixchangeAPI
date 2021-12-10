import random

from django.contrib.auth import login
import app.models as models
from django.contrib.auth.models import User
import datetime
from .app_utils.choices import *
from .app_utils.msg_manager import msg
from .app_utils.deals import find_best_deal
from .app_utils.market_order_manager import *

# REFERRAL 
def assign_rnd_btc(user,MIN=1,MAX=10):
    rnd = float(random.randint(MIN,MAX))
    user.profile.btc+= rnd
    user.save()
    return 
    
def validate_referral(registeringUser,rewardAmount = 5):
    sender = registeringUser.profile
    refcode= sender.usedReferral
    if refcode != "-----":
        refOwner= User.objects.filter(profile__ownReferral=refcode).first()
        if refOwner:
            refOwner = refOwner.profile
            send_referral_btc(sender, refOwner,rewardAmount)
            message = f"Referral code is valid! you and received 5 BTC !"
    
    else:message = msg.error(f"Invalid ref code ! {refcode}")
    return message

def send_referral_btc(sender,receiver,amount):
    new_transaction(sender,receiver,99,0,amount)
    return

#ORDERS


def place_order(placer,orderType, amount, USDprice):
    log = models.Log()
    if not is_order_type_valid(orderType):
        log.add(msg.error(f"Invalid order type ({orderType}). Order Canceled"))
        return log
    USDprice = 0  if orderType in [1,2] else USDprice #if market order, price =0 because will be set buy market offers
    #check balances
    if orderType in [1,3,5] and placer.usd < amount*USDprice: #cant buy
        log.add(msg.error(f"You dont have sufficent funds to cover your order at the moment\nOrder for {amount*USDprice}$ and {placer.usd}$ available"))
        newOrder = models.Order(placer=placer, type= orderType,USDprice = USDprice,amount=amount,status = 3)
        newOrder.save()
        return newOrder, log
    if orderType in [2,4,6] and placer.btc < amount: #sell
        newOrder = models.Order(placer=placer, type= orderType,USDprice = USDprice,amount=amount,status = 3)
        newOrder.save()
        log.add(msg.error(f"You dont have sufficent funds to cover your order at the moment\nOrder for {amount}BTC and {placer.btc} available"))
        return newOrder,log

    newOrder = models.Order(placer=placer, type= orderType,USDprice = USDprice,amount=amount)
    newOrder.save()
    usd,btc =placer.lock(newOrder)
    info = f"USD locked: {usd} , BTC locked: {btc}" if orderType not in [1,2] else  ""
    log.add(msg.info(info))
    newOrder.updateHistory("OPENED",info)
    log.add(msg.info(f"New {ORDER_TYPE_CHOICHES[orderType-1][1] } Order by: {placer.user.username} of {amount} btc at {USDprice}$ each has been placed with ID: {newOrder.id}!"))
    #check_for_orders_match(new_order)
    return newOrder,log

def check_for_orders_match(newOrder):
    '''Here is managed the logic behind the orders
    market order: order is entirely fulfilled as soon as possible, at the best price available
    limit_full, the order is matched only if is totally fulfilled by an other order, at the desired price or better
    limit_fast , the order is fulfilled, also partially , if a matching order at the correct price is available.
    the orders have differnt priority, the limit_full having the highest, followed by limit_fast and market'''

    log = models.Log()
    if newOrder.status != 1 :
        log.add(msg.nrm("Order not sent to market"))
        return log

    orderType= newOrder.type
    amountToCover = newOrder.amount

    if orderType in [1,3,5]: #buying
        msg.nrm("searching for BUY order match...")
        openOrders = models.Order.objects.filter(status=1 ).order_by("USDprice")  #only opens, by price ascending
        openOrders = openOrders.exclude(type=99)# \
        openOrders = openOrders.exclude(type=1) #  \
        openOrders = openOrders.exclude(type=3) #  | remove the other buy orders
        openOrders = openOrders.exclude(type=5) # /
        openOrders = openOrders.exclude(placer= newOrder.placer) #remove  own orders
        
        if orderType == 1: #1) market buy 
            marketBuyPool,usdNeeded =market_order_pool(newOrder,openOrders)
            if not marketBuyPool :
                log.add(msg.err_liquidity()) #no liquidity
                log.add(close_orders(3,newOrder)) #order fails
                return log
            else: #liquidity ok                       
                if usdNeeded > newOrder.placer.usd: #buyer has not enough usd to close the order 
                    log.add(msg.error(f"Insufficent funds to complete the order : {usdNeeded}$ needed and {newOrder.placer.usd}$ available"))
                    log.add(close_orders(3,newOrder)) #order fails
                    return log
                else:
                    log.add(msg.nrm(f"Funds sufficient : {usdNeeded}$ needed and {newOrder.placer.usd}$ available"))
                    log .add(unpack_market_pool(newOrder,marketBuyPool))
                    return log

        elif orderType == 3: #3 = limit fast buy
            openOrders= openOrders.filter(USDprice__lte = newOrder.USDprice).order_by("USDprice","-type","datetime")
            for order in openOrders:
                if newOrder.status == 1: #if order is still open, keep fulfilling it it
                    if order.type == 6: #full sell
                        if order.amount <= amountToCover: 
                            log.add(fulfill_order(newOrder,order))
                            continue
                        else: continue
                    elif order.type == 4: # sell order is fast
                            log.add(fulfill_order(newOrder,order))
                            continue
                return log
            log.add(msg.exchange_uncover(newOrder))
            return log

        elif orderType == 5: #5 limit buy full
            openOrdersFull= openOrders.filter(USDprice__lte = newOrder.USDprice,amount__lte=newOrder.amount ,type=6).order_by("USDprice","datetime")
            openOrdersFast = fillup_full_orders(newOrder, openOrders) 
            bestDeal = find_best_deal(newOrder,openOrdersFull)
            if not bestDeal:
                log.add(msg.exchange_uncover(newOrder))
                return log
            else:
                bestDeal.orderList += openOrdersFast
                for order in bestDeal.orderList:
                    if newOrder.status ==1: fulfill_order(order,newOrder)
                    else: return
            log.add(msg.error(f"Error fulfilling order id: {newOrder.id}"))
            return log
    #SELLING         
    elif orderType in [2,4,6]: #selling
        msg.nrm("searching for SELL order match...")
        openOrders = models.Order.objects.filter(status=1 ).order_by("-USDprice")  #only opens, by price descending
        openOrders = openOrders.exclude(type=99)# \
        openOrders = openOrders.exclude(type=2) #  \
        openOrders = openOrders.exclude(type=4) #  | remove the other sell orders
        openOrders = openOrders.exclude(type=6) # /
        openOrders = openOrders.exclude(placer = newOrder.placer) #remove mown orders
        if orderType == 2: #2) market sell 
            marketBuyPool,usdNeeded =market_order_pool(newOrder,openOrders)
            if marketBuyPool:
                log.add(msg.info(f"Found {len(marketBuyPool)} buy orders for you"))
                log.add(unpack_market_pool(newOrder,marketBuyPool))
                log.add(msg.ok(f"Order completed! sold {newOrder.amount}btc for {usdNeeded}$ of profit!"))
                return log
            else:
                log.add(msg.err_liquidity()) #no liquidity
                log.add(close_orders(3,newOrder)) #order fails   
                return log             
        
        elif orderType == 4: #4 = limit fast sell
            openOrders= openOrders.filter(USDprice__gte = newOrder.USDprice).order_by("-USDprice","-type","datetime")
            for order in openOrders:
                avgPrice = (order.USDprice + newOrder.USDprice )/2
                if newOrder.status == 1: #if order is still open, keep fulfilling it it
                    if order.type == 5: #full buy
                        if order.amount <= amountToCover and order.placer.usd >= order.amount*avgPrice: #buy order can be closed
                            log.add(fulfill_order(order,newOrder))
                            continue
                        else: continue
                    elif order.type == 3: # buy order is fast
                        log.add(fulfill_order(order,newOrder))
                        continue
            log.add(msg.exchange_uncover(newOrder))
            return log 

        elif orderType == 6: #6 limit buy full
            openOrdersFull= openOrders.filter(USDprice__gte = newOrder.USDprice,amount__lte=newOrder.amount ,type=5).order_by("-USDprice","datetime")
            openOrdersFast = fillup_full_orders(newOrder, openOrders) 
            print("Backup Orders : ",len(openOrdersFast))
            bestDeal = find_best_deal(newOrder,openOrdersFull)
            if not bestDeal:
                log.add(msg.exchange_uncover(newOrder))
                return log 
            else:
                bestDeal.orderList += openOrdersFast
                for order in bestDeal.orderList:
                    if newOrder.status ==1: log.add(fulfill_order(order,newOrder))
                    else: return log
            log.add(msg.error(f"Error fulfilling order id: {newOrder.id}"))
            return log


def fulfill_order(A_order,B_order):
    '''Takes 2 orders if one is buy type and the other is sell type, tries to close them . 
    Checks wether an order is to be closed (because fulfilled) or to be kept open (updated).
    creates the necessary transactions as well
    '''
    log=models.Log()
    if (A_order.type in [1,3,5] and B_order.type in [1,3,5]) or (A_order.type in [2,4,6] and B_order.type in [2,4,6]): #orders are of same kind. throw error
        log.add(msg.error(f"order id {A_order.id} is type {A_order.type }and order id  {B_order.id} is type {B_order.type}"))
        return log
    
    buyOrder = A_order if A_order.type in [1,3,5] else B_order
    sellOrder = A_order if A_order.type in [2,4,6] else B_order
    seller= sellOrder.placer #sender of btc (receiver of usd)
    buyer = buyOrder.placer #receiver of btc (sender of usd)   

    #the avg price is only if orders ar not market type,
    if buyOrder.type != 1 and sellOrder.type != 2:
        avgPrice = (buyOrder.USDprice + sellOrder.USDprice )/2 
    else: # the avg prive remains the one of the NOT-MARKET order
        avgPrice = buyOrder.USDprice if sellOrder.type == 2 else sellOrder.USDprice

    orderToClose = sellOrder if buyOrder.amount >= sellOrder.amount else buyOrder #the minor order will be closed
    orderToUpdate = sellOrder if orderToClose == buyOrder else buyOrder
    amountLeft = orderToUpdate.amount - orderToClose.amount

    #unlock usd
    if buyOrder.type != 1:
        lockedUsdForOrder = buyOrder.amount*buyOrder.USDprice
        usdToUnlock = lockedUsdForOrder- orderToClose.amount*avgPrice
        buyer.lock(mode=-1,usdToLock = usdToUnlock ) #unlock usd
        log.add(msg.nrm(f"Exchange saved you {usdToUnlock} !$"))
    if sellOrder.type != 2:
        #unlock btc
        seller.lock(mode= 1 ,btcToLock= orderToClose.amount) 
    else:
        seller.btc -= orderToClose.amount
    buyer.btc += orderToClose.amount
    usdCost = avgPrice*orderToClose.amount
    seller.usd += usdCost
    seller.profit += usdCost
    buyer.usd -= usdCost
    buyer.profit -= usdCost
    seller.save()
    buyer.save()

    log.add(new_transaction(seller,buyer,1,avgPrice,orderToClose.amount))
    if usdToUnlock : log.add(msg.nrm(f"Exchange saved you {usdToUnlock} !$"))
    
    log.add(close_orders(2,orderToClose))

    if amountLeft == 0 : #also the other order is to be closed
       log.add(close_orders(2,orderToUpdate))
    else:
        log.add(update_order(orderToUpdate,amountLeft))
    return log
 
def fillup_full_orders(newOrder,openOrders):
    '''Takes the orders of type FAST from the pool. Use the order to try to cover the full order.
    If there are not enough full order, Fast orders are used  '''
    if newOrder.type == 6:
        openOrders = openOrders.filter(USDprice__gte = newOrder.USDprice,type=3).order_by("-USDprice","amount","datetime")
    elif newOrder.type == 5:
        openOrders = openOrders.filter(USDprice__lte = newOrder.USDprice,type=4).order_by("USDprice","amount","datetime")
    amountNeeded = newOrder.amount
    ids=set()
    for order in openOrders:
        amountNeeded -= order.amount
        ids.add(order.id)
        if amountNeeded <= 0:
            break
    openOrders = openOrders.filter(id__in=ids)
    return openOrders

def update_order(orderToUpdate,newAmount):
    log=models.Log()
    log.add(msg.upt_ord_amt(orderToUpdate,newAmount))
    info=f"AMT {orderToUpdate.amount}->{newAmount}"
    orderToUpdate.amount = newAmount
    orderToUpdate.updateHistory("UPDATE",info)
    orderToUpdate.save()
    return log

def close_orders(status,*orders): #takes
    log = models.Log()
    for order in orders:
        order.status = status
        order.save()
        str_status = ORDER_STATUS_CHOICHES[status-1][1]
        order.updateHistory("CLOSED")
        log.add(msg.wrn(f"Order with id: {order.id} of type: {ORDER_TYPE_CHOICHES[order.type-1][1]} is now {str_status}"))
    return log
        

def cancel_order(order):
    log=models.Log()
    usd,btc=order.placer.lock(order=order,mode=-1)
    order.status=4
    order.save()
    info = f"{usd} USD - {btc} BTC Unlocked and returned to owner"
    log.add(msg.wrn(f"Order with id: {order.id} of type: {ORDER_TYPE_CHOICHES[order.type-1][1]} is now Canceled"))
    log.add(msg.wrn(info))
    order.updateHistory("CANCELLED",info)
    return True,log

# TRANSACTION
def new_transaction(sender,receiver,txType,USDprice,amount):
    log=models.Log()
    if txType == 99:
        new_transaction_referral(sender,receiver,amount)
        return
    new_transaction = models.Transaction(sender=sender,receiver = receiver, type= txType,USDprice = USDprice,amount=amount)
    new_transaction.totalUSD(amount,USDprice)
    new_transaction.save()
    log .add(msg.ok(f"New Transaction from:{sender.user.username} to {receiver.user.username} of {amount} btc at {USDprice}$ -> tot: {USDprice*amount}$ is Confirmed !"))
    return log

def new_transaction_referral(sender,receiver,amount):   #if referral
    USDprice =0
    sender.btc += amount
    receiver.btc += amount
    bank = models.Bank.objects.filter(id = 1).first()
    bank.treasure-= amount*2
    bank.save()
    receiver.save()
    sender.save()
    new_transaction = models.Transaction(sender=sender,receiver = receiver, type= 99,USDprice = USDprice,amount=amount)
    new_transaction.save()
    msg.ok(f"Valid Referral Code: {sender.user.username} \nUser : {receiver.user.username} will receive {amount} BTC and be vey happy")
    return

