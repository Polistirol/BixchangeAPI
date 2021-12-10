
import random
import requests
import json

from requests.sessions import session
import interface as i

class Site:
    url ='http://127.0.0.1:8000/console'
    session =  requests.Session()
    i = random.randint(0,100)

global url 

global site
site = Site()

def ping(address=None):
    try:
        if address:
            site.url = address
        requests.get(Site.url)
        return True
    except Exception as e:
        print(e)
        return False

def post(param):
    url = Site().url
    post = site.session.post(url = url,data=param)
    return post.text

def close():
    site.session.close()

def login(param):
    param["action"]="login"
    response = post(param)
    response = json.loads(response)
    if response["logged"]:
        #user logged

        return param["username"],response["id"]
    else:
        return False,False

def new_order(param):
    param["action"]="new_order"
    response = post(param)
    response = json.loads(response)
    return response["log"]

def get_balance(user):
    param = {"action":"balance",
        "user_id":user.id}
    response = post(param)
    balance = json.loads(response)
    del balance["Orders"]
    return balance

def get_orders(user):
    param = {"action":"orders",
    "user_id":user.id}
    response = post(param)
    orders = json.loads(response)
    fullOrdersDetails = orders.pop("Full Orders Details")
    return orders,fullOrdersDetails

def cancel_order(id):
    param = {"action":"cancel","order_id":id}    
    response = post(param)
    response = json.loads(response)
    if response["success"]:
        print(response["log"])
    else:
        i.msg.error(f"There was a problem canceling your order !")

def get_exchange_overview():
    param = {"action":"overview"}
    response = post(param)
    overview = json.loads(response)
    return overview 

def get_traders_overview():
    param = {"action":"traders"}
    response = post(param)
    overview = json.loads(response)
    return overview 

def get_btc_market_price():
    param = {"action":"get_btc_price"}
    response = post(param)
    response = json.loads(response)
    price = response["succes"]
    try:
        price = float(price)
        return price
    except:
        i.msg.error(response["log"])
        return None
