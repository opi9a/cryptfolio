# get coins, vols, prices (other stuff?)

# check for history
# - of each coin
# - find last date (or start date as min)
from datetime import datetime
import pandas as pd
import os

hist_start = datetime(2014,1,1)
# get tickers


# fill in history
# - make list of missing days
#   - get last day
#   - make list form last+1 to yesterday
# - api call for each (may as well get all coins)

#!/home/gav/anaconda3/python3

import requests
import json
import cryptfolio as cf

# Function takes a list of ticker symbols and a UTC timestamp
# returns dict with symbols and prices



def get_hist(tickers, timestamp):
    '''Returns a dictionary of coins with 1/price in GBP
    '''
    base = '''https://min-api.cryptocompare.com/data/pricehistorical?fsym=GBP&tsyms='''
    ticks=",".join(tickers)
    ts="".join(["&ts=", str(timestamp)])
    url = "".join([base, ticks, ts])
    req = requests.get(url).text
    return json.loads(req)['GBP']                      


def get_tickers(coins):
	ticks = []
	for c in coins:
		req=requests.get("".join(["https://api.coinmarketcap.com/v1/ticker/",c,"/"])).text
		tick = json.loads(req)[0]['symbol']
		ticks.append(tick)
	return ticks

# try:
# 	hist_df = pd.read_csv('price_history.csv')
# except:
# 	hist_df = get_hist(get_tickers(coins), hist_start)


interval = 24*60*60 #eg this is seconds per ~day~


# if history file exists:
    # get last datestamp, else input hardcoded start datestamp

start = 1452680500 # last date + interval (eg + 1 day)
outs = []
         
# work out the range of dates to yesterday (or today midnight?)
# eg for i in range(start, yday, interval):
# or while date < today - probably better

# NB on cryptocompare, bitcoin cash is 'BCH'
             
for i in range(10):
    ts = start + (i*interval)
    x = get_hist(['BTC','ETH'],ts)
    outs.append(x)
    