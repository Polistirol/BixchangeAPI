# colors table @ https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    MAGENTA = '\033[35m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class msg:
    def wrn(text):
        text_ = bcolors.WARNING + text + bcolors.ENDC
        print(text_)
        return text
    def error(text):
        text_ = bcolors.FAIL + text + bcolors.ENDC
        print(text_)
        return text
    def ok(text):
        text_ = bcolors.OKGREEN + text + bcolors.ENDC
        print(text_)
        return text
    def nrm(text):
        print(text)
        return text
    def info(text):
        text_ = bcolors.OKCYAN + text + bcolors.ENDC
        print(text_)
        return text
    def info2(text):
        text_ =bcolors.MAGENTA + text + bcolors.ENDC 
        print(text_)
        return text
    def bold(text):
        text_ = bcolors.BOLD + text +bcolors.ENDC
        print(text_)
        return text
    def underline(text):
        text_ = bcolors.UNDERLINE+text+bcolors.ENDC
        print(text_)
        return text

    def no_funds(order):
        msg.error(f"You dont have sufficent funds to cover your order at the moment\n")
        msg.info(f"But the order is now live in the market. Order ID :{order.id} ")

    def exchange_uncover(order):
        a= msg.wrn(f"The Exchange can't entirely fulfill this order at the moment..")
        b = msg.info(f"But the order is now live in the market. Order ID :{order.id} ")
        return a+"\n"+b

    def err_liquidity():
        return msg.error(f"Insufficent exchange liquidity to satisfy this order  ")

    def bold(text):
        return bcolors.BOLD+text+bcolors.ENDC

    def upt_ord_amt(orderToUpdate,newAmount):
        return msg.info(f"Order id: {orderToUpdate.id} has been updated:AMOUNT: from {orderToUpdate.amount}btc to -> {newAmount}btc at {orderToUpdate.USDprice}$")
         

    def upt_ord_usd(orderToUpdate,newAmount):
        return msg.info(f"Order id: {orderToUpdate.id} has been updated:: from {orderToUpdate.amount}btc to -> {newAmount}btc at {orderToUpdate.USDprice}$ ")
