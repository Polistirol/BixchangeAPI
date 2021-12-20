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


def assign_rnd_btc(user, MIN=1, MAX=10):
    rnd = float(random.randint(MIN, MAX))
    user.profile.btc += rnd
    user.save()
    print(f"New User {user} received {rnd} BTC upon registration")
    return


def validate_referral(registeringUser, rewardAmount=5):
    sender = registeringUser.profile
    refcode = sender.usedReferral
    if refcode != "-----":
        refOwner = User.objects.filter(profile__ownReferral=refcode).first()
        if refOwner:
            refOwner = refOwner.profile
            send_referral_btc(sender, refOwner, rewardAmount)
            return f"Referral code is valid! you and received 5 BTC !"
    message = msg.error(f"Invalid ref code ! {refcode}")
    return message


def send_referral_btc(sender, receiver, amount):
    new_transaction(sender, receiver, 99, 0, amount)
    return

# ORDERS


def place_order(placer, orderType, amount, USDprice):
    if not is_order_type_valid(orderType):
        return msg.error(f"Invalid order type ({orderType}). Order Canceled")

    # if market order, price =0 because will be set buy market offers
    USDprice = 0 if orderType in [1, 2] else USDprice
    # check balances
    if orderType in [1, 3, 5] and placer.usd < amount*USDprice:  # cant buy
        newOrder = models.Order(placer=placer, type=orderType,
                                USDprice=USDprice, amount=amount, openingAmount=amount, status=3)
        newOrder.save()
        newOrder.updateHistory(msg.error(
            f"You dont have sufficent funds to cover your order at the moment: Order for {amount*USDprice}$ and {placer.usd}$ available"))
        return newOrder

    if orderType in [2, 4, 6] and placer.btc < amount:  # sell
        newOrder = models.Order(placer=placer, type=orderType,
                                USDprice=USDprice, amount=amount, openingAmount=amount, status=3)
        newOrder.save()
        newOrder.updateHistory(msg.error(
            f"You dont have sufficent funds to cover your order at the moment: Order for {amount}BTC and {placer.btc} available"))
        return newOrder

    newOrder = models.Order(placer=placer, type=orderType,
                            USDprice=USDprice, amount=amount, openingAmount=amount)
    newOrder.save()
    usd, btc = placer.lock(newOrder)
    lockInfo = f"USD locked: {usd} , BTC locked: {btc}" if orderType not in [
        1, 2] else "Market order, nothing is locked"
    if newOrder.type in [1, 2]:
        newInfo = msg.info(
            f"New {ORDER_TYPE_CHOICHES[orderType-1][1] } Order by: {placer.user.username} of {amount} btc at Market Price has been placed with ID: {newOrder.id}!")
    else:
        newInfo = msg.info(
            f"New {ORDER_TYPE_CHOICHES[orderType-1][1] } Order by: {placer.user.username} of {amount} btc at {USDprice}$ each has been placed with ID: {newOrder.id}!")
    newOrder.updateHistory("OPENED", newInfo, lockInfo, "-----")
    # check_for_orders_match(new_order)
    return newOrder


def check_for_orders_match(newOrder):
    '''Here is managed the logic behind the orders
    market order: order is entirely fulfilled as soon as possible, at the best price available
    limit_full, the order is matched only if is totally fulfilled by an other order, at the desired price or better
    limit_fast , the order is fulfilled, also partially , if a matching order at the correct price is available.
    the orders have differnt priority, the limit_full having the highest, followed by limit_fast and market'''

    if newOrder.status != 1:
        newOrder.updateHistory(msg.nrm("Order not sent to market"))
        return newOrder

    orderType = newOrder.type
    amountToCover = newOrder.amount

    if orderType in [1, 3, 5]:  # buying
        msg.nrm("searching for BUY order match...")
        openOrders = models.Order.objects.filter(status=1).order_by(
            "USDprice")  # only opens, by price ascending
        openOrders = openOrders.exclude(type=99)  # \
        openOrders = openOrders.exclude(type=1)  # \
        openOrders = openOrders.exclude(
            type=3)  # | remove the other buy orders
        openOrders = openOrders.exclude(type=5)  # /
        openOrders = openOrders.exclude(
            placer=newOrder.placer)  # remove  own orders

        if orderType == 1:  # 1) market buy
            marketBuyPool, usdNeeded = market_order_pool(newOrder, openOrders)
            if not marketBuyPool:
                newOrder.updateHistory(msg.err_liquidity())  # no liquidity
                close_orders(3, newOrder)
                return newOrder
            else:  # liquidity ok
                if usdNeeded > newOrder.placer.usd:  # buyer has not enough usd to close the order
                    newOrder.updateHistory(msg.error(
                        f"Insufficent funds to complete the order : {usdNeeded}$ needed and {newOrder.placer.usd}$ available"))
                    close_orders(3, newOrder)  # order fails
                    return newOrder
                else:
                    newOrder.updateHistory(msg.nrm(
                        f"Funds sufficient : {usdNeeded}$ needed and {newOrder.placer.usd}$ available"))
                    unpack_market_pool(newOrder, marketBuyPool)
                    newOrder.updateHistory(msg.ok(
                        f"Order completed! bought {newOrder.openingAmount}btc for {usdNeeded}$ !"))
                    return newOrder

        elif orderType == 3:  # 3 = limit fast buy
            openOrders = openOrders.filter(USDprice__lte=newOrder.USDprice).order_by(
                "USDprice", "-type", "datetime")
            for order in openOrders:
                if order.type == 6:  # full sell
                    if order.amount <= amountToCover:
                        fulfill_order(newOrder, order)
                    else:
                        continue
                elif order.type == 4:  # sell order is fast
                    fulfill_order(newOrder, order)
                if newOrder.status != 1:
                    return  # if order is still open, keep fulfilling it it
            newOrder.updateHistory(msg.exchange_uncover(newOrder))
            return

        elif orderType == 5:  # 5 limit buy full
            # Get all FULL orders
            openOrdersFull = openOrders.filter(
                USDprice__lte=newOrder.USDprice, amount__lte=newOrder.amount, type=6).order_by("USDprice", "datetime")
            # get coverage orders orders
            coverageOrders, amountAviableFromCoverage = get_coverage_orders(
                newOrder, openOrders)
            print("coverage ", len(coverageOrders))
            # combine the full orders available to get the best deal for the new order
            bestDeal = find_best_deal(
                newOrder=newOrder, ordersFull=openOrdersFull)
            if not bestDeal or bestDeal.amountLeft > amountAviableFromCoverage:
                newOrder.updateHistory(msg.exchange_uncover(newOrder))
                return
            else:
                bestDeal.orderList += coverageOrders
                for order in bestDeal.orderList:
                    fulfill_order(order, newOrder)
                    if newOrder.status != 1:
                        return
            newOrder.updateHistory(
                msg.error(f"Error fulfilling order id: {newOrder.id}"))
            return
    # SELLING
    elif orderType in [2, 4, 6]:  # selling
        msg.nrm("searching for SELL order match...")
        openOrders = models.Order.objects.filter(status=1).order_by(
            "-USDprice")  # only opens, by price descending
        openOrders = openOrders.exclude(type=99)  # \
        openOrders = openOrders.exclude(type=2)  # \
        openOrders = openOrders.exclude(
            type=4)  # | remove the other sell orders
        openOrders = openOrders.exclude(type=6)  # /
        openOrders = openOrders.exclude(
            placer=newOrder.placer)  # remove mown orders
        if orderType == 2:  # 2) market sell
            marketBuyPool, usdNeeded = market_order_pool(newOrder, openOrders)
            if marketBuyPool:
                msg.info(f"Found {len(marketBuyPool)} buy orders for you")
                unpack_market_pool(newOrder, marketBuyPool)
                newOrder.updateHistory(msg.ok(
                    f"Order completed! sold {newOrder.openingAmount}btc for {usdNeeded}$ of profit!"))
                return newOrder
            else:
                newOrder.updateHistory(msg.err_liquidity())  # no liquidity
                close_orders(3, newOrder)  # order fails
                return newOrder

        elif orderType == 4:  # 4 = limit fast sell
            openOrders = openOrders.filter(USDprice__gte=newOrder.USDprice).order_by(
                "-USDprice", "-type", "datetime")
            for order in openOrders:
                avgPrice = (order.USDprice + newOrder.USDprice)/2
                if order.type == 5:  # full buy
                    if order.amount <= amountToCover and order.placer.usd >= order.amount*avgPrice:  # buy order can be closed
                        fulfill_order(order, newOrder)
                    else:
                        continue
                elif order.type == 3:  # buy order is fast
                    fulfill_order(order, newOrder)
                if newOrder.status != 1:
                    return  # if order is still open, keep fulfilling it it
            newOrder.updateHistory(msg.exchange_uncover(newOrder))
            return

        elif orderType == 6:  # 6 limit sell full
            openOrdersFull = openOrders.filter(
                USDprice__gte=newOrder.USDprice, amount__lte=newOrder.amount, type=5).order_by("-USDprice", "datetime")
            coverageOrders, amountAviableFromCoverage = get_coverage_orders(
                newOrder, openOrders)
            bestDeal = find_best_deal(newOrder, openOrdersFull)
            if not bestDeal or bestDeal.amountLeft > amountAviableFromCoverage:
                newOrder.updateHistory(msg.exchange_uncover(newOrder))
                return
            else:
                bestDeal.orderList += coverageOrders
                for order in bestDeal.orderList:
                    fulfill_order(order, newOrder)
                    # newOrder.updateHistory(order.message)
                    if newOrder.status != 1:
                        return
            newOrder.updateHistory(
                msg.error(f"Error fulfilling order id: {newOrder.id}"))
            return


def fulfill_order(A_order, B_order):
    '''Takes 2 orders if one is buy type and the other is sell type, tries to close them . 
    Checks wether an order is to be closed (because fulfilled) or to be kept open (updated).
    creates the necessary transactions as well
    '''
    if (A_order.type in [1, 3, 5] and B_order.type in [1, 3, 5]) or (A_order.type in [2, 4, 6] and B_order.type in [2, 4, 6]):  # orders are of same kind. throw error
        msg.error(
            f"order id {A_order.id} is type {A_order.type }and order id  {B_order.id} is type {B_order.type}")
        return

    buyOrder = A_order if A_order.type in [1, 3, 5] else B_order
    sellOrder = A_order if A_order.type in [2, 4, 6] else B_order
    seller = sellOrder.placer  # sender of btc (receiver of usd)
    buyer = buyOrder.placer  # receiver of btc (sender of usd)
    # the avg price is only if orders ar not market type,
    if buyOrder.type != 1 and sellOrder.type != 2:
        avgPrice = (buyOrder.USDprice + sellOrder.USDprice)/2
    else:  # the avg prive remains the one of the NOT-MARKET order
        avgPrice = buyOrder.USDprice if sellOrder.type == 2 else sellOrder.USDprice

    # the minor order will be closed
    orderToClose = sellOrder if buyOrder.amount >= sellOrder.amount else buyOrder
    orderToUpdate = sellOrder if orderToClose == buyOrder else buyOrder
    amountLeft = orderToUpdate.amount - orderToClose.amount

    # unlock usd
    if buyOrder.type != 1:
        lockedUsdForOrder = orderToClose.amount*buyOrder.USDprice
        usdToUnlock = lockedUsdForOrder - orderToClose.amount*avgPrice
        buyer.lock(mode=-1, usdToLock=usdToUnlock)  # unlock usd
        saved = msg.nrm(
            f"The market found a deal at {avgPrice}$ insted of {buyOrder.USDprice}$, a total of {usdToUnlock}$ was saved !")
        if usdToUnlock > 0:
            buyOrder.updateHistory(saved)

    if sellOrder.type == 2:
        seller.btc -= orderToClose.amount
    else:
        seller.lockedBTC -= orderToClose.amount

    buyer.btc += orderToClose.amount
    usdCost = avgPrice*orderToClose.amount
    seller.usd += usdCost
    seller.profit += usdCost
    buyer.usd -= usdCost
    buyer.profit -= usdCost
    buyOrder.dollarProfit -= usdCost
    sellOrder.dollarProfit += usdCost
    seller.save()
    buyer.save()
    txLog = new_transaction(seller, buyer, 1, avgPrice, orderToClose.amount)
    buyOrder.updateHistory(txLog)
    sellOrder.updateHistory(txLog)
    close_orders(2, orderToClose)
    if amountLeft == 0:  # also the other order is to be closed
        close_orders(2, orderToUpdate)
    else:
        update_order(orderToUpdate, amountLeft)
    return


def get_coverage_orders(newOrder, openOrders):
    '''Coverage orders are orders of type LIMIT_FAST that are used as a backup, 
    in case there is no liquidity amoung the FULL orders to fulfill a new FULL order.'''
    if newOrder.type == 6:
        openOrders = openOrders.filter(USDprice__gte=newOrder.USDprice, type=3).order_by(
            "-USDprice", "amount", "datetime")
    elif newOrder.type == 5:
        openOrders = openOrders.filter(USDprice__lte=newOrder.USDprice, type=4).order_by(
            "USDprice", "amount", "datetime")
    amountNeeded = newOrder.amount
    amountAviableFromCoverage = 0
    ids = set()
    for order in openOrders:
        amountNeeded -= order.amount
        amountAviableFromCoverage += order.amount
        ids.add(order.id)
        if amountNeeded <= 0:
            break
    coverageOrders = openOrders.filter(id__in=ids)
    return coverageOrders, amountAviableFromCoverage


def update_order(orderToUpdate, newAmount):
    msg.upt_ord_amt(orderToUpdate, newAmount)
    info = f"UPDATE : AMOUNT {orderToUpdate.amount}->{newAmount}"
    orderToUpdate.amount = newAmount
    orderToUpdate.updateHistory(info)
    orderToUpdate.save()
    return


def close_orders(status, *orders):  # takes
    for order in orders:
        order.status = status
        order.amount = 0
        order.save()
        str_status = ORDER_STATUS_CHOICHES[status-1][1]
        infoMsg = msg.wrn(
            f"Order with id: {order.id} of type: {ORDER_TYPE_CHOICHES[order.type-1][1]} is now {str_status}")
        order.updateHistory(infoMsg, "--END--")
    return


def cancel_order(order):
    usd, btc = order.placer.lock(order=order, mode=-1)
    order.status = 4
    order.save()
    unlockedMsg = f"{usd} USD - {btc} BTC Unlocked and returned to owner"
    cancelledMsg = msg.wrn(
        f"Order with id: {order.id} of type: {ORDER_TYPE_CHOICHES[order.type-1][1]} was Canceled by the User")
    order.updateHistory(unlockedMsg, cancelledMsg, "--END--")
    return True

# TRANSACTION


def new_transaction(sender, receiver, txType, USDprice, amount):
    if txType == 99:
        txLog = new_transaction_referral(sender, receiver, amount)
        return txLog
    new_transaction = models.Transaction(
        sender=sender, receiver=receiver, type=txType, USDprice=USDprice, amount=amount)
    new_transaction.totalUSD(amount, USDprice)
    new_transaction.save()
    txLog = msg.ok(
        f"TRANSACTION : New Transaction from:{sender.user.username} to {receiver.user.username} of {amount} btc at {USDprice}$ -> tot: {USDprice*amount}$ is Confirmed !")
    return txLog


def new_transaction_referral(sender, receiver, amount):  # if referral
    USDprice = 0
    sender.btc += amount
    receiver.btc += amount
    bank = models.Bank.objects.filter(id=1).first()
    bank.treasure -= amount*2
    bank.save()
    receiver.save()
    sender.save()
    new_transaction = models.Transaction(
        sender=sender, receiver=receiver, type=99, USDprice=USDprice, amount=amount)
    new_transaction.save()
    txLog = msg.ok(
        f"Valid Referral Code: {sender.user.username} \nUser : {receiver.user.username} will receive {amount} BTC and be vey happy")
    return txLog
