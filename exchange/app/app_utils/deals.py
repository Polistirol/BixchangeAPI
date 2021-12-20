from .msg_manager import msg
# Create your tests here.


class Deal:
    '''This class is used to find the best deals for orders of type LIMIT FULL.
    it combines all the compatible orders on the platforms and compute the most lucrative combination.
    if no compatible combination is found. injects orders of type LIMIT FAST and use them to fulfill the order
    '''

    def __init__(self, ID, orderList, total):
        self.id = ID
        self.total = total
        self.orderList = orderList
        self.finalPrice = 0
        self.amountLeft = 0
        self.saved = 0
        self.message = ""

    def __str__(self):
        ids = [order.id for order in self.orderList]
        string = f"ID: {self.id}, Total= {self.id} \nnOrders Included; {len(self.orderList)} {ids} \nAmount left: {self.amountLeft}"
        return string

    def getFinalPrice(self, askedPrice, targetAmount, orderType):
        if self.orderList:
            for order in self.orderList:
                self.finalPrice += abs(((order.USDprice +
                                       askedPrice) / 2) * order.amount)
            saved = self.saved = abs(askedPrice*targetAmount - self.finalPrice)
            if orderType == "buy":
                self.message = msg.ok(
                    f"Final price is {self.finalPrice}! \n{saved}$ saved from {askedPrice*targetAmount}$ asked!\n")
            else:
                self.message = msg.ok(
                    f"Final price is {self.finalPrice}! \n{saved}$ extra earned from {askedPrice*targetAmount}$ asked!\n")
            return self
        else:
            self.message = msg.error(
                "Order list not found while getting final price")


def generate(orders: list, target, partial=[], partial_sum=0, orderlist=[]):
    if partial_sum == target:
        yield partial
    if partial_sum >= target:
        return
    for index, order in enumerate(orders):
        remaining = orders[index + 1:]
        yield from generate(remaining, target, partial + [order], partial_sum + order.amount)


def get_best_deal(generator, orderType):
    deals = []
    totScanned = 0
    for index, ordersList in enumerate(generator):
        totScanned += 1
        fullPrice = 0
        for order in ordersList:
            fullPrice += order.amount * order.USDprice
        deals.append(Deal(index, ordersList, fullPrice))
    msg.info(f"Scanned {totScanned} valid combinations")
    if deals:
        bestDeal = deals[0]
        bestDealPrice = deals[0].total
        for d in deals:
            if orderType == "buy":
                if d.total < bestDealPrice:
                    bestDealPrice = d.total
                    bestDeal = d
            elif orderType == "sell":
                if d.total > bestDealPrice:
                    bestDealPrice = d.total
                    bestDeal = d
        return bestDeal
    else:
        msg.error("No deals")
        return


def use_backup(ordersFull, targetAmount, orderType):
    print("need backup")
    newBestDeal = []
    i = 1
    while not newBestDeal:
        print("recycling with target =", targetAmount - i)
        generator = generate(ordersFull, targetAmount-i)
        newBestDeal = get_best_deal(generator, orderType)
        i += 1
        if i == targetAmount:
            return None
    newBestDeal.amountLeft = i-1
    return newBestDeal


def find_best_deal(newOrder, ordersFull, maxLenOrder=50) -> list:
    ''' Returns the list of orders with the best deal for the order maker.'''
    targetAmount = newOrder.amount
    askedPrice = newOrder.USDprice
    orderType = "sell" if newOrder.type == 6 else "buy"

    # this filter is temporay, is used to prevent performance issue
    ordersFull = ordersFull if len(
        ordersFull) < maxLenOrder else ordersFull[:maxLenOrder]
    generator = generate(ordersFull, targetAmount)

    bestDeal = get_best_deal(generator, orderType)

    if bestDeal:
        bestDeal = bestDeal.getFinalPrice(askedPrice, targetAmount, orderType)
    else:  # if cant get cover with full orders, add fast order as backup
        bestDeal = use_backup(ordersFull, targetAmount, orderType)
    return bestDeal
