import interface as i
import service_console as scs
from user import User
import json
from requests.exceptions import RequestException
import sys



def connect(address="http://127.0.0.1:8000/console"):
    i.msg.info("Connecting to the servr...")
    isConnected= scs.ping(address)
    if not isConnected:
        i.msg.error("Connection Failed. \nImpossible to reach the Server")
        _quit()
    else:
        i.msg.ok("Connected to the server !")
        i.msg.ok(f"---> {address}")
        return

def _quit():
    scs.close()
    print("Quitting..See you soon!")
    quit()

def login():
    while True:
        param = i.ask_login_credentials()
        if not param:
            _quit()
        username,user_id= scs.login(param)
        if username and user_id : 
            i.msg.ok(f"Login successful!")
            user = User(username,user_id,param["pw"])
            i.msg.info2(f"Welcome {username}!\nWhat would you like to do from here ?" )
            break
        else: i.msg.error("Username or Password Invalid!\nTry again")
    return user
    
def filterOrdersByStatus(ordersList,status):
    ordersOfStatus = []
    if not status: #status is none so X was pressed to go back
        return ordersOfStatus
    else:
        for order in ordersList:
            for ID,data in order.items():
                if data["Order Status"]==status:
                    ordersOfStatus.append(order)
        return ordersOfStatus

def filterOrdersByType(ordersList,orderType):
    ordersOfType = []
    if not orderType: #type is none so X was pressed to go back
        return ordersOfType
    else:
        for order in ordersList:
            for ID,data in order.items():
                if data["Order Type"]==orderType:
                    ordersOfType.append(order)
        return ordersOfType

def filterOrdersByID(ordersList,orderID) ->list:
    
    if not orderID: #type is none so X was pressed to go back
        return None
    else:
        orderWithID = []
        for order in ordersList:
            for ID,data in order.items():
                if ID == orderID:
                    orderWithID.append(order)
                    return orderWithID
        i.msg.error(f"NO Order with ID: {ID}")
        return None

def ordersMainMenu(ordersDict):
    while True:
        r=i.orders_main_menu()
        if r == "a":#display all
            i.display_all_orders(ordersDict)
            break
        if r == "s": #explore by status
            status = i.choose_order_status() #ask what status to filter by
            ordersOfStatus = filterOrdersByStatus(ordersDict, status) #filters the orders
            i.msg.wrn(f"____{status.upper()} ORDERS____")
            i.display_all_orders(ordersOfStatus) #display the orders

        elif r == "t": #explore by type
            _type = i.choose_orders_type() #ask what type to filter by
            ordersOfType = filterOrdersByType(ordersDict,_type)
            i.msg.wrn(f"____{_type.upper()} ORDERS____")
            i.display_all_orders(ordersOfType)

        elif r== "m":
            ID = i.choose_order_id()
            orderWithID = filterOrdersByID(ordersDict,ID)
            i.msg.wrn(f"____{ID} ____")
            #i.display_all_orders(orderWithID)
            if orderWithID: 
                orderStatus = i.display_single_order(orderWithID)
                if orderStatus == "Open": #if order is open, ask what user wants to do
                    option = i.single_order_options(ID,status ="Open") 
                    if option == "c" : #cancel selected order, send to svc the input
                        scs.cancel_order(ID)
        elif r=="x":
            homeMenu(user)

        homeMenu(user,r="o")

def homeMenu(user,r=None):
    if not r:
        r = i.home_menu()

    if r == "b": #get balance 
       userInfoDict= scs.get_balance(user)
       i.print_user_balance(userInfoDict)

    elif r == "o" : #get orders
        ordersOverview,fullOrdersDetails = scs.get_orders(user)
        i.print_user_orders_overview(ordersOverview)  
        ordersMainMenu(fullOrdersDetails)

    elif r=="n": #make new order
        btcMarketPrice = scs.get_btc_market_price()
        params = i.get_new_order_data(btcMarketPrice)
        if params:
            params["user_id"] = user.id
            response = scs.new_order(params)
            i.pp(response)
        homeMenu(user= user,r="o")

    elif r=="e":#exchange overview
        exchangeOverview = scs.get_exchange_overview()
        i.msg.wrn("____EXCHANGE OVERVIEW____")
        i.pp(exchangeOverview)

    elif r=="t":#exchange overview
        tradersOverview = scs.get_traders_overview()
        i.msg.wrn("____TRADERS OVERVIEW____")
        i.pp(tradersOverview)

    elif r =="q":
        i.msg.wrn("Are you sure to quit? \n[Y] to confirm\n[N] to stay")
        r = input("").lower().strip()
        if r=="y" :
            _quit()
    homeMenu(user)



try:
    i.msg.init() 
    
    if len(sys.argv) ==2: 
        connect(sys.argv[1])
    else:
        connect()
    i.welcome()
    user = login()
    if user:
        homeMenu(user)
except RequestException as e:  
    i.msg.error("Connection Lost !\n Check your connection or try again later !")
    _quit()
