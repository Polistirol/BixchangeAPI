# BixchangeAPI
###Bitcoin web Exchange + console App


Test Version 0.1

## The Exchange
BixChange is a Bitcoin exchange API/website, built with Python 3.8, Django and MongoDB and a series of complementary libraries\
It allows registered users tu trade Bitcoin and retrive general informations about the stat of the exchange

## Trading
User can issue various types of Buy and Sell orders:

### Market Orders
Set the amount of BTC you'd like to buy or sell.\
We will immediately search the market for the best rates !\
A Market orderd will be **either** fulfilled entirely and immediately, or it will be canceled.
### Limit FAST Orders
Set the amount of BTC and the $ price of each.\
The market will look for the optimal deals for your order.\
We will try to fulfill it enirely, if that is impossible: the order will be fulfilled as much as possible, the **un-fulfilled** amount will remain active on the market, waiting for an optimal match.
### Limit FULL Orders
Set the amount of BTC and the $ price of each.\
The market will search for a way to fulfill it enirely, if that is impossible at the moment, your **whole** order will be published on the market.\
A Limit FULL order will **never be splitted**, it will be either entirely fulfilled or be public on the market, waiting for an optimal deal

# Console app
Console app usage:\
Download the folder Console-App from this repo\
from terminal run:
```
python core.py https://df1d-151-60-30-251.ngrok.io
```
