from typing import Text
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
import app.services_app as svc
from .app_utils.choices import *
import datetime
import string
import random

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usd = models.FloatField(default=100)
    btc = models.FloatField(default=0)
    lockedUSD = models.FloatField(default=0)
    lockedBTC = models.FloatField(default=0)
    ownReferral = models.CharField(max_length=5, default="-----")
    usedReferral = models.CharField(max_length=5, default="-----")
    profit = models.FloatField(default=0)

    def lock(self, order=None, mode=1, usdToLock=0, btcToLock=0, ):
        '''Lock/Unlock assets from an order, or given as argument.
        The Mode parameter set if is locking( mode = 1) or unlocking (mode =-1) '''
        if order:
            if order.type in [3, 5]:  # buy order, so lock max usd
                usdToLock = order.amount*order.USDprice*mode
                self.lockedUSD += usdToLock
                self.usd -= usdToLock
            elif order.type in [4, 6]:  # sell order, so lock max btc
                btcToLock = order.amount*mode
                self.lockedBTC += btcToLock
                self.btc -= btcToLock
        else:
            self.lockedUSD += usdToLock*mode
            self.lockedBTC += btcToLock*mode
            self.usd -= usdToLock*mode
            self.btc -= btcToLock*mode
        self.save()
        return abs(usdToLock), abs(btcToLock)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        while True:
            newRefCode = ''.join(random.choice(
                string.ascii_letters + string.digits) for i in range(5))
            isUsed = Profile.objects.filter(ownReferral=newRefCode).first()
            if isUsed:
                print("ref used, regenearatring")
            else:
                break

        instance.profile.ownReferral = newRefCode
        instance.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Order(models.Model):
    placer = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, related_name="placer", null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(choices=ORDER_TYPE_CHOICHES, default=1)
    USDprice = models.FloatField(default=0)
    amount = models.FloatField(default=0)
    openingAmount = models.FloatField(default=0)
    dollarProfit = models.FloatField(default=0)
    status = models.IntegerField(choices=ORDER_STATUS_CHOICHES, default=1)
    history = models.JSONField(default=dict)

    def updateHistory(self, *args):
        now = str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
        if now in self.history.keys():
            for arg in args:
                self.history[now].append(arg)
        else:
            self.history[now] = []
            for arg in args:
                self.history[now].append(arg)
        self.save()


class Transaction(models.Model):
    sender = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, related_name="sender", null=True)
    receiver = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, related_name="receiver", null=True)
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, related_name="order", null=True)
    type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICHES, default=1)
    amount = models.FloatField(default=0)
    USDprice = models.FloatField(default=0)
    totalUSDvalue = models.FloatField(default=0)
    datetime = models.DateTimeField(auto_now_add=True)

    def totalUSD(self, amount, price):
        return amount*price


class Bank(models.Model):
    currency = models.CharField(max_length=20)
    treasure = models.FloatField(default=100000)
    treasureUSD = models.FloatField(default=10000)
    globalMarketPrice = models.FloatField(default=0)
    lockedBTCtot = models.FloatField(default=0)
    vol24H = models.FloatField(default=0)
    volTot = models.FloatField(default=0)
    lockedUSDtot = models.FloatField(default=0)

    def updateStats(self, lockedBTCtot, lockedUSDtot, volTot, vol24H):
        self.lockedBTCtot = lockedBTCtot
        self.lockedUSDtot = lockedUSDtot
        self.volTot = volTot
        self.vol24H = vol24H
        self.save()

    def updatePrice(self, newPrice):
        self.globalMarketPrice = newPrice
        self.save()


class Log():
    '''Logs every interaction with the database/site, every message is an item of a list'''

    def __init__(self) -> None:
        self.content = []

    def add(self, msg):
        '''Append a message to the log list, if msg is of type LOG, Log.append method will be run'''
        if isinstance(msg, Log):
            self.append(msg)
        else:
            self.content.append(msg)

    def append(self, log):
        '''Joins the passed log to the caller log, appending all the messages.'''
        for msg in log.content:
            self.content.append(msg)

    def __str__(self) -> str:
        return str(self.content)
