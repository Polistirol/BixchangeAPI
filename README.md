# BixchangeAPI
### Bitcoin web Exchange + console App


Test Version LIVE @ https://bixchangeapi.loca.lt/
\
BixChange is a Bitcoin exchange API/website, built with:
- [Python 3.9](https://www.python.org/downloads/release/python-391/)
- [Django Web Framework - v3.2.9](https://www.djangoproject.com/)
- [MongoDB -Database](https://www.mongodb.com/) 
- [Djongo -MDB Mapper - v1.3.6](https://www.djongomapper.com/)
- and a series of complementary libraries, a full list can be checked [here](requirements.txt)\

# The Exchange

It allows registered users to trade Bitcoin and retrive general informations about the status of the exchange
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
Users may prefer to use a console application, in order to adopt a more programmable use of the exchange\
***It is required to the user to be registered through the website first***

Console app usage:\
Download `BixChangeConsole.exe` inside `Console-App` from this repo\
from terminal, locate the downloaded BixChangeConsole.exe and run

```
BixChangeConsole.exe https://bixchangeapi.loca.lt/
```
The argument states the url of the web-app\
If omitted, the console will connect to https://127.0.0.1:8000, the default Django address while prototyping


The console features a text-based interface and all the offers unique interactions with the exchange, such as the possibility to manually close own orders.

 ## Deploy
 You can follow these steps to deploy Bixchange on your machine !
### Prerequisites
You need same pieces of software before start, click on the links to get to the official installation page:
- [MongoDB community Edition](https://docs.mongodb.com/manual/installation/)
- [Python](https://www.python.org/downloads)
- Verify that `pip` and `virtualenv` are also installed
 ```pip --version```
 ```virtualenv --version```

### Setup local machine
For semplicity, let's create a starting folder called bixchangeeDeploy, anywhere in your system\
```
mkdir bixchangeeDeploy
```
then let's get into it and download or clone this repository inside\
```
cd bixchangeeDeploy
git clone https://github.com/Polistirol/BixchangeAPI.git
```
Then create a virtual eviroment using\
```
python -m venv mdbenv
```
And activate it\
Windows:
``` 
mdbenv\Scripts\activate.bat
```\
Linux/Ubuntu : 
```
source mdbenv/bin/activate
```
Now install all the packages needed using pip and requirements.txt\
(from now on, the paths are written in Windows format)  
```
pip install -r BixchangeAPI\requirements.txt
```
When it's done, let's initialize the database with django
```
python .\exchange\manage.py makemigrations
python .\exchange\manage.py migrate
```
let's create the first user
python .\exchange\manage.py createsuperuser
```
and follow the prompted instruction\ 
Finally run the app
```
python .\exchange\manage.py runserver
```
Now use your browser to go to:
``` http://127.0.0.1:8000/ ``` and there you go !

