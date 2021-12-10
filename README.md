# BixchangeAPI
### Bitcoin web Exchange + console App


Test Version 0.1

# The Exchange
BixChange is a Bitcoin exchange API/website, built with Python 3.8, Django and MongoDB and a series of complementary libraries\
\
It allows registered users to trade Bitcoin and retrive general informations about the stat of the exchange
### New Users
To every new user a random amount of BTC (ranging from 1 to 10..so pretty big money here) is sent\
***When registering, use a valid referral code for extra 5 BTC to you and your referred friend!***

## API 
The main web page offers quick ways to retrive data from the platform, this data is serialized into JSON format.\
### Your Balance
Explore in details your wallet Balance and all your Orders details.
### Exchange Overview
Have an overview of this exchange: daily Volume, active Orders and more
### Traders
See how fellow traders are going
## Trading
User can issue various types of Buy and Sell orders:

### Market Orders
Users set the amount of BTC they'd like to buy or sell.\
The exchange will then immediately search the market for the best rates\
A Market orderd will be **either** fulfilled entirely and immediately, or it will be canceled.
### Limit FAST Orders
Set the amount of BTC and the $ price of each.\
The market will look for the optimal deals for the order.\
And it will try to fulfill it enirely, if that is impossible: the order will be fulfilled as much as possible, the **un-fulfilled** amount will remain active on the market, waiting for an optimal match.
### Limit FULL Orders
Set the amount of BTC and the $ price of each.\
The market will search for a way to fulfill it enirely, if that is impossible at the moment, the **whole** order will be published on the market.\
A Limit FULL order will **never be splitted**, it will be either entirely fulfilled or be public on the market, waiting for an optimal deal

# Console app
Users to use a console version of the exchange\
***It is required to the user to be registered through the website first***

Console app usage:\
Download the folder `Console-App` from this repo\
from terminal: navigate inside the downloaded `Console-App` and run:
```
python core.py https://df1d-151-60-30-251.ngrok.io
```
The console app offers unique interactions with the exchange, such as the possibility to manually close own orders
