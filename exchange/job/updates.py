import builtins
from django.utils import timezone
import requests
from app.models import Bank, Profile, Order
import datetime


def fetchDataFromApi():
    try:
        # get from api eth and btc over USD
        urlCJ = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        dataFromAPI = requests.get(url=urlCJ).json()
        coins = list(dataFromAPI.keys())
        newPrice = dataFromAPI[coins[0]]["usd"]
        bank, created = Bank.objects.get_or_create(currency="bitcoin")
        if created:
            print("A new Bank was created!")
        bank.updatePrice(newPrice)
        return
    except Exception as e:
        print("price Not updated", e)


def getBankStats(currency="bitcoin"):
    bank, _ = Bank.objects.get_or_create(currency=currency)
    yesterday = datetime.datetime.now(
        tz=timezone.utc) - datetime.timedelta(days=1)
    lockedBTCtot = sum(
        [profile.lockedBTC for profile in Profile.objects.all()])
    lockedUSDtot = sum(
        [profile.lockedUSD for profile in Profile.objects.all()])
    volTot = sum([order.openingAmount -
                 order.amount for order in Order.objects.all().filter(status=2)])
    vol24H = sum([order.openingAmount - order.amount for order in Order.objects.all(
    ).filter(status=2, datetime__gte=yesterday)])
    bank.updateStats(lockedBTCtot=lockedBTCtot,
                     lockedUSDtot=lockedUSDtot, volTot=volTot, vol24H=vol24H)
