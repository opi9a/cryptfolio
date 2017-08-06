#!/home/gav/anaconda3/python3

from datetime import datetime
import pandas as pd
import requests
import json
import cryptfolio as cf


tnow = int((datetime.now() - datetime(1970,1,1)).total_seconds())

coin_data=get_data(depth=50)

# TODO update historical data, get ydays prices
# TODO 'too many figures' warning from matplotlib. 
# Being closed on reload?

# get coins and vols, and tickers of coins
# CURRENTLY HAVE PLACEHOLDERS FOR YDAY PRICES
coins, vols = cf.get_coins('config.txt')
ticks = cf.get_tickers(coins)
# TODO Make ticks a dict, to assoc with coin name (poss in index)
main_df=pd.DataFrame(vols, index=ticks, columns=['vols'])
main_df=main_df.join(1/(cf.get_now_prices(ticks).T))
main_df['price_change']=main_df['prices'] - 99 # last_price
main_df['values']=main_df['vols']*main_df['prices']
main_df['val_change']=main_df['price_change']*main_df['vols']
total=sum(main_df['values'])
main_df['shares']=main_df['values']/total
       
caps={}
for c in ticks:
    for d in coin_data:
        if d['symbol'] == c:
            caps[c]=float(d['market_cap_gbp'])

# TODO check there is btc in order to calc weight       
main_df=main_df.join(pd.Series(caps,name='caps'))
btc_proportion=main_df.loc['BTC','values']/main_df.loc['BTC','caps']
main_df['weight']=((main_df['values']/main_df['caps'])/btc_proportion)
main_df['£PPPW']=btc_proportion*main_df['caps']*0.01

# display table f(coins, prices_today, prices_yday, vols)

# display historical graph

# watch out for changes in order - do lookups by name not index

hist_start = int((datetime(2017,7,7)-datetime(1970,1,1)).total_seconds())
day_s = 24*60*60 #eg this is seconds per ~day~

# need to process ticks in batch of 7 (or query max)
# do this in get_hist

try:
    hist_df = pd.read_csv('price_history.csv', index_col=0)
except:
    hist = cf.get_hist(ticks, hist_start)
    hist_df = pd.DataFrame(hist, [hist_start])

time_point = hist_df.iloc[-1].name + day_s
#
while time_point < tnow:
    print(time_point)
    hist_df=hist_df.append(cf.get_hist(ticks,time_point))
    time_point += day_s


    