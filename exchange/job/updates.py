from django.utils import timezone
import requests
from app.models import Bank,Profile,Order
import datetime

def fetchDataFromApi():
    try:
        urlCJ= "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd" #get from api eth and btc over USD
        dataFromAPI = requests.get(url = urlCJ).json()
        coins = list(dataFromAPI.keys())
        newPrice = dataFromAPI[coins[0]]["usd"]
        bank = Bank.objects.get(currency="bitcoin")
        bank.updatePrice(newPrice)
        return 
    except Exception as e:
        print("price Not updated",e)



def getBankStats(currency="bitcoin"):
    bank = Bank.objects.get(currency=currency)
    yesterday = datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days = 1)
    lockedBTCtot = sum([profile.lockedBTC for profile in Profile.objects.all()])
    lockedUSDtot = sum([profile.lockedUSD for profile in Profile.objects.all()])
    volTot = sum(order.amount for order in Order.objects.all().filter(status=2))/2
    vol24H = sum(order.amount for order in Order.objects.all().filter(status=2,datetime__gte=yesterday))/2
    bank.updateStats(lockedBTCtot=lockedBTCtot,lockedUSDtot=lockedUSDtot , volTot = volTot , vol24H = vol24H)




