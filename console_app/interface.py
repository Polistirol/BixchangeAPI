import os
import pprint
from tabulate import tabulate
import random


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
    def init():
        '''Enables the color output from the console '''
        os.system("powershell write-host -fore White ") 

    def wrn(text):
        text = bcolors.WARNING + text + bcolors.ENDC
        print(text)
        return text
    def error(text):
        text = bcolors.FAIL + text + bcolors.ENDC
        print(text)
        return text
    def ok(text):
        text = bcolors.OKGREEN + text + bcolors.ENDC
        print(text)
        return text
    def nrm(text):
        print(text)
        return text
    def info(text):
        text = bcolors.OKCYAN + text + bcolors.ENDC
        print(text)
        return text
    def info2(text):
        text =bcolors.MAGENTA + text + bcolors.ENDC 
        print(text)
        return text
    def bold(text):
        text = bcolors.BOLD + text +bcolors.ENDC
        print(text)
        return text
    def underline(text):
        text = bcolors.UNDERLINE+text+bcolors.ENDC
        print(text)
        return text

class OrderType:
    typeDict = {
    1:"Buy_Market",
    2:"Sell_Market",
    3:"Buy_Limit_Fast",
    4:"Sell_Limit_Fast",
    5:"Buy_Limit_Full",
    6:"Sell_Limit_Full",
    99:"Referral"} 

    statusDict = {1:"Open",
                2:"Closed",
                3:"Failed",
                4:"Canceled"}



def welcome():
    logo ='''@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&                                  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@                  @@@  .              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@              @@@, @@@  @@@              (@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@               ,(@@@@@@@@@@%               *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@,   @@@@@                  @@@@@  .%@@@@@(            %@@@@@@@@@@@@@.   @@@@@@@@@@@@@
@@@@@@@@@@@@    @@@@@@@@                 ,@@@@      @@@@@,            @@@@@@@@@@@@@@@@    @@@@@@@@@@
@@@@@@@@@.   @@@@@@@@@@(                 @@@@@@@&%@@@@@@@             @@@@@@@@@@@@@@@@@@@,   @@@@@@@
@@@@@@@@    @@@@@@@@@@@(                @@@@@  ,&@@@@@@               @@@@@@@@@@@@@@@@@@@&   /@@@@@@
@@@@@@@@@@@    @@@@@@@@@                @@@@,      &@@@@@             @@@@@@@@@@@@@@@@&   #@@@@@@@@@
@@@@@@@@@@@@@@    @@@@@@,           @@@@@@@@(.    ,@@@@@#            @@@@@@@@@@@@@@#   #@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@ @@@@@@@               @@@@@@@@@@@@@@@.            #@@@@@@@@@@@@@@@%@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@,             @@( ,@@,                   %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@                &@@                  .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'''

    randomColor = random.randint(1,5)
    print(randomColor)
    if randomColor == 1:
        msg.error(logo)
    elif randomColor == 2:
        msg.info(logo)
    elif randomColor == 3:
        msg.info2(logo)
    elif randomColor == 4:
        msg.wrn(logo)
    elif randomColor == 5:
        msg.ok(logo)
    elif randomColor == 6:
        msg.nrm(logo)
    msg.info("WELCOME TO THE CONSOLE APP")


def pp(content):
    pprint.pprint(content,sort_dicts=False,width=160)

def print_user_balance(userInfoDict):
    msg.wrn(f"___{userInfoDict['username']}___")
    for key in userInfoDict:
        msg.info(key+" : "+str(userInfoDict[key]))

def print_user_orders_overview(ordersDict):
    msg.wrn(f"___Orders Overview___")
    for key in ordersDict:
        msg.info(key+" : "+str(ordersDict[key]))

def ask_login_credentials():
    while True:
        r = input("Press L to [L]ogin\nPress Q to [Q]uit\n").strip().lower()
        if r =="l": break
        elif r =="q": return False
        msg.error("Invalid choice, try again")
    #asking credentials
    username = input("Enter username: ")
    pw1 = input("Password: ")
    param = {"username": username , "pw":pw1}   
    return  param

def home_menu():
    while True:
        msg.wrn("_____HOME MENU_____")
        msg.nrm("Press B to check your [B]alance")
        msg.nrm("Press O to check your [O]rders")
        msg.nrm("Press N to make a [N]ew order ")
        msg.nrm("Press E for the [E]xchange overview ")
        msg.nrm("Press T for the [T]raders overview ")
        msg.nrm("Press Q to [Q]uit the program")
        r = input("").strip().lower()
        if r in ["b","o","n","q","e","t"]:
            break
        else:
            msg.error("invalid choice! try again")
    return r

def orders_main_menu():
    while True:
        msg.wrn("_____EXPLORE ORDERS_____")
        msg.nrm("Press A to display [A]ll")
        msg.nrm("Press S to filter by [S]tatus")
        msg.nrm("Press T to filter by [T]ype")
        msg.nrm("press M to [M]anage single orders")
        msg.nrm("press X to go back")
        r= input("").strip().lower()
        if r in ["a","s","t","m","x"]:
            break
        else:
            msg.error("invalid choice! try again")
    return r

def choose_order_status():
    while True:
        msg.wrn("_____Choose order status_____")
        msg.nrm("Press O for your [O]pen orders")
        msg.nrm("Press C for your [C]losed orders")
        msg.nrm("Press F for your [F]ailed orders")
        msg.nrm("Press N for your ca[N]celed orders") 
        msg.nrm("press X to go back")
        r= input("").strip().lower()
        if r == "o" : return "Open"
        elif r == "c" : return "Closed"   
        elif r == "f" : return "Failed"  
        elif r == "n" : return "Canceled" 
        elif r == "x" : return None   
        else:
            msg.error("invalid choice! try again")

def choose_orders_type(returnNumber=False):
    while True:
        msg.wrn("_____Choose order type_____")
        msg.nrm("Press 1 for your BUY-Market orders")
        msg.nrm("Press 2 for your SELL-Market orders")
        msg.nrm("Press 3 for your BUY-Limit fast orders")
        msg.nrm("Press 4 for your SELL-Limit Fast orders") 
        msg.nrm("Press 5 for your BUY-Limit Full orders") 
        msg.nrm("Press 6 for your SELL-Limit Full orders") 
        msg.nrm("press X to go back")
        r= input("").strip().lower()
        
        if r in ["1","2","3","4","5","6","99"] :
            orderType =OrderType.typeDict[int(r)]
            break
        elif r == "x" : 
            orderType= None 
            break
        else:
            msg.error("invalid choice! try again")
 
    return orderType if not returnNumber else r

def choose_order_id():
    msg.wrn("__SINGLE ORDER__")
    while True:
        r = input("Order ID ? (X to cancel)  ").lower().strip()
        try:
            int(r)
            return r
        except ValueError :
            if r == "x":
                msg.error("Operation canceled")
                return False
            else:
                msg.error("Invalid choice! Try Again")     

def display_all_orders(orders):
    if not orders:
        msg.error("No order found !")
    else:
        pp(orders)

def display_single_order(order):
    order = order[0]
    for ID,data in order.items():
        msg.bold(f"Order ID : {ID}")
        msg.nrm(f"Made the:  {data['Date']}")
        msg.info2(f"Type: {data['Order Type'] }")
        msg.wrn(f"BTC opening amount: {data['Opening Amount']}")
        msg.wrn(f"BTC amount left: {data['Amount Left']}")
        msg.ok(f"At {data['USD Price']}$ ")
        status = data['Order Status']
        if status == "Open":
            msg.ok(f"STATUS : {data['Order Status'] }")
        elif status == "Closed":
            msg.error(f"STATUS : {data['Order Status'] }")
        else: 
            msg.info2(f"STATUS : {data['Order Status'] }")
        msg.bold("HISTORY:")
        pp(data['History'])
        msg.nrm("\n")
    return status

def single_order_options(ID,status):
    while True:
        if status == "Open":
            r = input("Press C to [C]ancel this order - [X] to go back  ").strip().lower()
            if r=="c":
                msg.wrn(f"Order :{ID} will be Canceled")
                msg.wrn("Are you sure? [Y]es\[N]o")
                confirmed  =input("").lower().strip()
                if confirmed == "y": return r
                else: 
                    msg.error("Operation aborted")
                    return False
            elif r=="x": return False
            else: msg.error("Invalid choice !")
        else:
            break
    return False
    

def get_new_order_data(btcPrice):
    while True: #get type
        orderType = choose_orders_type(returnNumber=True)
        if orderType == "x":
            msg.error("Order aborted")
            return False
        else:
            break
    while True: #get amount
        msg.info("how many BTC ?")
        amount = input("").lower().strip()
        try:
            amount = float(amount)
            if amount >0 : break
            else: raise ValueError
        except ValueError :
            msg.error("invalid amount")  
    if orderType not in ["1","2"]:display_btc_market_price(btcPrice)
    while True: #get price
        if orderType not in ["1","2"]:
            msg.info("\nAt what price each- US$ ?")
            USDprice = input("").lower().strip()
            try:
                USDprice = float(USDprice)
                if USDprice >0 : break
                else: raise ValueError
            except ValueError :
                msg.error("invalid amount")  
        else:
            USDprice = 0
            break
    msg.wrn(f"New order of type: {OrderType.typeDict[int(orderType)]} for {amount} BTC at {USDprice}$ each\n CONFIRM? [Y]es\[N]o ")  
    confirmed = input("").lower().strip()
    if confirmed == "y":
        return {"type":orderType,"amount":amount,"USDprice":USDprice}  
    else:
        msg.error("Order aborted")
        return False

def display_btc_market_price(price):
    p = price/100
    p1 = price + p * 1
    p5 = price + p * 5
    p10 =price + p *10
    pm1 =price - p * 1
    pm5 =price - p * 5
    pm10=price - p*10 

    a = bcolors.FAIL+"-10%"+ bcolors.ENDC
    b=bcolors.FAIL+"-5%"+ bcolors.ENDC
    c=bcolors.FAIL+"-1%"+ bcolors.ENDC
    d=bcolors.OKBLUE+"PRICE"+bcolors.ENDC
    e= bcolors.OKGREEN+"+1%"+bcolors.ENDC
    f=bcolors.OKGREEN+"+5%"+bcolors.ENDC
    g=bcolors.OKGREEN+"+10%"+bcolors.ENDC
    headers =[a, b , c ,d ,e,f,g]
    table = [[pm10,pm5,pm1,price,p1,p5,p10]]
    msg.wrn("Price Suggestions in $ of 1 BTC")
    msg.nrm(tabulate(table, headers, tablefmt="github"))


