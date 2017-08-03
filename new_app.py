#!/home/gav/anaconda3/python3

# CRYPTOCOMPARE ONLY ACCEPTS 7 COINS

from datetime import datetime
import pandas as pd
import requests
import json
import cryptfolio as cf

hist_start = int((datetime(2017,7,7)-datetime(1970,1,1)).total_seconds())
day_s = 24*60*60 #eg this is seconds per ~day~
coins, vols = cf.get_coins('config.txt')
ticks = cf.get_tickers(coins)


try:
    hist_df = pd.read_csv('price_history.csv', index_col=0)
except:
    hist = cf.get_hist(ticks, hist_start)
    hist_df = pd.DataFrame(hist, [hist_start])

time_point = hist_df.iloc[-1].name + day_s
tnow = int((datetime.now() - datetime(1970,1,1)).total_seconds())

while time_point < tnow:
    print(time_point)
    hist_df=hist_df.append(cf.get_hist(ticks,time_point))
    time_point += day_s


    