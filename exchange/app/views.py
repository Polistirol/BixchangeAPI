#from django.db.models.fields import Field
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from .forms import NewUserForm
from django.contrib import messages
from django.utils import timezone
from .models import *
import app.services_app as svc
from .app_utils.serializer import serialize_balance, serialize_exchange_info, serialize_orders, serialize_traders
import json
import datetime


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            svc.assign_rnd_btc(user)  # assign to new user 1-10 btc
            # checks if referral code is valid and distribute the rewards
            message = svc.validate_referral(user)
            user.save()
            return redirect("/", context={"message": "Registraton successful\n"+message})
        print("Error registering")
        messages.error(
            request, "Unsuccessful registration. Invalid information.")
        return redirect("/", context={"message": "Unsuccessful registration. Invalid information."})

    form = NewUserForm()
    return render(request=request, template_name="app/register.html", context={"register_form": form})


@csrf_exempt
def console(request):
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "login":
            userID = console_login(request)
            if userID:
                response = {"id": userID, "logged": True}
            else:
                response = {"id": None, "logged": False}
            return JsonResponse(response, safe=False)
        else:
            if not request.user.is_authenticated:
                print("User Not logged")
                return HttpResponse("USER NOT Logged !")
            else:
                print("User logged")
                if action == "balance":
                    userID = request.POST.get("user_id", None)
                    user = User.objects.get(id=userID)
                    profile_json = serialize_balance(user)
                    return JsonResponse(profile_json, safe=False)

                elif action == "orders":
                    userID = request.POST.get("user_id", None)
                    user = User.objects.get(id=userID)
                    orders_json = serialize_balance(user)["Orders"]
                    return JsonResponse(orders_json, safe=False)

                elif action == "overview":
                    overview_json = serialize_exchange_info()
                    return JsonResponse(overview_json, safe=False)

                elif action == "traders":
                    traders_json = serialize_traders()
                    return JsonResponse(traders_json, safe=False)

                elif action == "cancel":
                    orderId = request.POST.get("order_id", None)
                    orderToCancel = Order.objects.all().get(id=orderId)
                    if orderToCancel:
                        isSucess = svc.cancel_order(orderToCancel)
                        if isSucess:
                            return JsonResponse({"action": "cancel", "success": True, "log": f"Order {orderId} was successfully Canceled!"}, safe=False)
                        else:
                            return JsonResponse({"action": "cancel", "success": False, "log": "There was a problem canceling your order !"}, safe=False)
                    else:
                        print("Order not found")
                        return JsonResponse({"action": "cancel", "succes": False, "log": "Order not found"}, safe=False)

                elif action == "new_order":
                    userID = request.POST.get("user_id", None)
                    profile = User.objects.get(id=userID).profile
                    orderType = int(request.POST.get("type", None))
                    amount = float(request.POST.get("amount", None))
                    USDprice = float(request.POST.get("USDprice", None))
                    newOrder = svc.place_order(
                        profile, orderType, amount, USDprice)
                    if newOrder:
                        svc.check_for_orders_match(newOrder)
                        log = serialize_orders([newOrder])
                    return JsonResponse({"action": "new_order", "log": log}, safe=False)

                elif action == "get_btc_price":
                    price = Bank.objects.get(
                        currency="bitcoin").globalMarketPrice
                    if price:
                        return JsonResponse({"action": "get_btc_price", "succes": price, "log": ""}, safe=False)
                    else:
                        return JsonResponse({"action": "get_btc_price", "succes": None, "log": "Failed to fetch price"}, safe=False)
    else:
        return JsonResponse({"Failed": "Invalid request Type!"}, safe=False)


def console_login(request):
    username = request.POST.get("username", None)
    password = request.POST.get("pw", None)
    user = authenticate(username=username, password=password)
    login(request, user)
    print(request.user)
    if user:
        print(f"User {user.username} with ID: {user.id} logged from console")
        return user.id
    # A backend authenticated the credentials
    else:
        print("no user")
        return False
    # No backend authenticated the credentials


def balance(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login")
    user = request.user
    profile_json = serialize_balance(user)
    return JsonResponse(profile_json, safe=False)


def exchangeOverview(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login")
    overview_json = serialize_exchange_info()
    return JsonResponse(overview_json, safe=False)


def api(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login")
    user2 = User.objects.filter(username="test").first().profile
    price = Bank.objects.get(currency="bitcoin").globalMarketPrice
    user = request.user
    # Order.objects.all().delete()
    # test_orders(user2)
    # resetOrders()
    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "balance":
            profile_json = serialize_balance(user)
            return JsonResponse(profile_json, safe=False)
        if action == "overview":
            overview_json = serialize_exchange_info()
            return JsonResponse(overview_json, safe=False)
        if action == "traders":
            test_orders(user2)
            traders_json = serialize_traders()
            return JsonResponse(traders_json, safe=False)
        if action == "BUY" or action == "SELL":
            orderType = int(request.POST.get("field", None))
            if action == "SELL":
                orderType += 1
            amount = float(request.POST.get("amount", None))
            USDprice = float(request.POST.get("USDprice", None))
            print(request.POST)
            newOrder = svc.place_order(
                user.profile, orderType, amount, USDprice)
            if newOrder:
                svc.check_for_orders_match(newOrder)
            return order_id(request=request, id=newOrder.id, log=newOrder.history)

    return render(request=request, template_name="app/api.html", context={"esito": None, "globalPrice": price, "profile": user.profile})


def order_id(request, id, log=None):
    order = Order.objects.get(id=id)
    order_json = serialize_orders([order])
    if log:
        order_json.insert(0, {"Placement Log": log})
    return JsonResponse(order_json, safe=False)


def resetOrders():
    openOrders = Order.objects.filter(status=2)
    for order in openOrders:
        order.status = 1
        order.save()


def test_orders(user):
    # (1, ("Buy_Market")),
    # (2,("Sell_market")),
    # (3,("Buy_Limit_fast")),
    # (4,("Sell_limit_fast")),
    # (5,("Buy_Limit_full")),
    # (6,("Sell_limit_full"))
    Order.objects.all().delete()
    # newOrder = svc.place_order(user,4,3,5)
    # newOrder = svc.place_order(user,4,2,6)
    # newOrder = svc.place_order(user,4,6,6)
    # newOrder = svc.place_order(user,4,7,6)
    # newOrder = svc.place_order(user,4,10,7)

    # newOrder = svc.place_order(user,6,4,3)
    # newOrder = svc.place_order(user,6,5,5)
    # newOrder = svc.place_order(user,6,10,5)
    # newOrder = svc.place_order(user,6,1,6)

    # newOrder = svc.place_order(user,3,5,7)
    # newOrder = svc.place_order(user,3,4,7)
    # newOrder = svc.place_order(user,3,3,6)
    # newOrder = svc.place_order(user,3,2,4)

    # newOrder = svc.place_order(user,5,5,8)
    # newOrder = svc.place_order(user,5,5,7)
    # newOrder = svc.place_order(user,5,3,5)
    # newOrder = svc.place_order(user,5,2,6)

    newOrder = svc.place_order(user, 3, 5, 6)
    newOrder = svc.place_order(user, 3, 10, 8)
    newOrder = svc.place_order(user, 5, 3, 7)
