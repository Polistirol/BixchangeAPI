from datetime import date
from django.utils import timezone
from app.models import *
from .choices import *
from job.updates import getBankStats


def serialize_balance(user):
    profile = user.profile
    output = {
        "ID": user.id,
        "username": user.username,
        "Own referral code": profile.ownReferral,
        "USD available": profile.usd,
        "BTC available": profile.btc,
        "Locked USD": profile.lockedUSD,
        "Locked BTC": profile.lockedBTC,
        "Profit": profile.profit,
        "Orders": serialize_user_orders(user)
    }
    return output


def serialize_user_orders(user):
    output = {}
    orders = Order.objects.all().filter(placer=user.profile).order_by("datetime")
    if not orders:
        return no_orders()
    output = {"Orders Placed": len(orders),
              "Open Orders": orders.filter(status=1).count(),
              "Closed Orders": orders.filter(status=2).count(),
              "Failed Orders": orders.filter(status=3).count(),
              "Canceled Orders": orders.filter(status=4).count(),
              "Full Orders Details": serialize_orders(orders=orders)
              }
    return output


def serialize_orders(orders):
    output = []
    for order in orders:
        singleOrderData = {
            "Date": order.datetime,
            "Order Type":  ORDER_TYPE_CHOICHES[order.type-1][1],
            "Opening Amount": order.openingAmount,
            "Amount Left": order.amount,
            "Asked USD for BTC unit": order.USDprice if order.USDprice != 0 else "Market Price",
            "USD order value": order.dollarProfit,
            "Order Status": ORDER_STATUS_CHOICHES[order.status-1][1],
            "History": order.history}
        singleOrder = {str(order.id): singleOrderData}
        output.append(singleOrder)
    return output


def serialize_exchange_info():
    getBankStats()
    bank = Bank.objects.all().first()

    output = {
        "Currency": bank.currency,
        "Currency Global Price": bank.globalMarketPrice,
        "BTC Total Value Locked": bank.lockedBTCtot,
        "USD Total Value Locked": bank.lockedUSDtot,
        "BTC treasuere": bank.treasure,
        "USD treasure": bank.treasureUSD,
        "--------": "",
        "24h Volume": bank.vol24H,
        "Total Volume": bank.volTot,
        "Total Transactions": Transaction.objects.all().count(),
        "Last Transaction": Transaction.objects.all().order_by("datetime").first().datetime if Transaction.objects.all().count() else "No Transaction so far",
        "Total Orders": Order.objects.all().count(),
        "Status": {"Open": Order.objects.filter(status=1).count(),
                   "Closed": Order.objects.filter(status=2).count(),
                   "Failed": Order.objects.filter(status=3).count(),
                   "Canceled": Order.objects.filter(status=4).count(),
                   },
        "Type": {ORDER_TYPE_CHOICHES[0][1]: Order.objects.filter(type=1).count(),
                 ORDER_TYPE_CHOICHES[1][1]: Order.objects.filter(type=2).count(),
                 ORDER_TYPE_CHOICHES[2][1]: Order.objects.filter(type=3).count(),
                 ORDER_TYPE_CHOICHES[3][1]: Order.objects.filter(type=4).count(),
                 ORDER_TYPE_CHOICHES[4][1]: Order.objects.filter(type=5).count(),
                 ORDER_TYPE_CHOICHES[5][1]: Order.objects.filter(type=6).count(),
                 ORDER_TYPE_CHOICHES[6][1]: Order.objects.filter(type=99).count(),
                 },
    }
    return output


def serialize_traders():
    yesterday = datetime.datetime.now(
        tz=timezone.utc) - datetime.timedelta(days=1)
    last = Order.objects.all().order_by("datetime").first()
    if not last:
        return no_orders()
    last = serialize_orders([last])
    output = {
        "Active Users": Profile.objects.all().count(),
        "Top profit": Profile.objects.all().exclude(user__username="BankTestMM").order_by("-profit").first().profit,
        "Worst Profit": Profile.objects.all().order_by("profit").first().profit,
        "New Orders Today": Order.objects.all().filter(datetime__gte=yesterday).count(),
        "Last": last
    }
    return output


def no_orders():
    output = {
        "Warning": "No order found! "
    }
    return output
