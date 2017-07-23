#!/home/gav/anaconda3/python3

import urllib.request
import json
from tkinter import *
from tkinter.font import Font
import datetime

def get_coins(conf="config.txt"):  
    '''Parses a config file to find coin names and numbers of units
    Returns two lists:  the coin names and the numbers of units (aka vols)
    '''
    c, v = [],[]  
    with open(conf, "r") as f:
        i = 0
        for line in f:
            if line[0] != "#":
                c.append(line.split()[0])
                v.append(float(line.split()[1]))
                i+=1
    return c, v

def get_data(target = "long_return.txt"):
    source = "https://api.coinmarketcap.com/v1/ticker/?convert=GBP&limit=45"
    urllib.request.urlretrieve(source, target)
    with open(target) as data_file:
        data = json.load(data_file)       
    return data

def get_prices(coins, datafile):
    prices = []
    for coin in coins:
        for entry in datafile:
            if entry['id'] == coin:
                prices.append(float(entry['price_gbp']))
    return prices

def calc_values(coins, vols, prices):  
    values, total = [], 0.0
    for i,coin in enumerate(coins):
        value=vols[i]*float(prices[i])
        values.append(value)
        total = total + value    
    return values, total

def calc_shares(values, total):
    shares = []    
    for i,value in enumerate(values):
        shares.append(value/total)
    return shares

def get_total_mkt():
    targeturl = "https://api.coinmarketcap.com/v1/global/?convert=GBP"
    with urllib.request.urlopen(targeturl) as response:
        raw_data = response.read()

    # that gives a bytes array, which needs to be converted to a string 
    # before using json.loads on it

    string = raw_data.decode("utf-8")
    data = json.loads(string)
       
    return data["total_market_cap_gbp"]

def get_coin_caps(coins, datafile):
    caps = []
    for coin in coins:
        for entry in datafile:
            if entry['id'] == coin:
                caps.append(float(entry['market_cap_gbp']))
    return caps    

def mk_dict(coins, vols, prices, values, shares, caps):

    for i, coin in enumerate(coins):
        if coin == "dogecoin":
            coins[i] = "dogecoin (000)"
            prices[i] = prices[i] * 1000
            vols[i] = vols[i] / 1000

    out_dict={}
    for i, coin in enumerate(coins):
        out_dict[coin]=[]
        out_dict[coin].append(prices[i])
        out_dict[coin].append(vols[i])
        out_dict[coin].append(values[i])
        out_dict[coin].append(shares[i]*100)
        out_dict[coin].append(100*(values[i] / caps[i])/(values[0]/caps[0]))
        out_dict[coin].append(0.01*(values[0]/caps[0])*caps[i])
    return out_dict

def print_folio2(coin_dict, total):
    print("")
    print(str(datetime.datetime.now()).split(".")[0])
    
    len1 = len(max(coin_dict.keys(), key=len))+2
    pad = 13

    print("\nCOIN".ljust(len1+1), end="")
    for title in ("PRICE UNITS VALUE SHARE WEIGHT £PPPW").split():
        print(title.rjust(pad), end="")
    
    for coin in coin_dict:
        print("")
        print(coin.ljust(len1), end = "")
        for i in range(len(coin_dict[coin])):
            print("{:>0,.2f}".format(coin_dict[coin][i]).rjust(pad), end="")

    print("\n\nTOTAL", " "*37, "{:10,.0f}".format(total))
    print("(non bitcoin)", " "*27,  "({:10,.0f})".format(total-coin_dict['bitcoin'][2]))
    print("")

def crypt_get(config_file):
    coins, vols = get_coins(config_file)
    data = get_data()
    prices = get_prices(coins, data)
    if len(coins) == len(prices):
        values, total = calc_values(coins, vols, prices)
        shares = calc_shares(values, total)
        caps = get_coin_caps(coins, data)
        #total_mkt_cap = get_total_mkt()
        coin_dict = mk_dict(coins, vols, prices, values, shares, caps)
        
    else:
        print("\nOK so I've got {} coins and {} prices.".format(len(coins), len(prices)))
        print("\nThe coins are", " ".join(coins))
        print("\nThe prices are", " ".join(str(x)[:5] for x in prices))
        print("\nThat probably means a coin has dropped out of the top 20, which \
is how many coins are retrieved.  This should be fixed in a future \
version but for now, could look in code to find the call to the \
coinmarket.cap api, and change the 'limit' argument")
    return coin_dict, total

def get_blockh():
    with urllib.request.urlopen('https://blockchain.info/q/getblockcount') as f:
        h = int(f.read())

    return h


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        config_file = sys.argv[1]
    else:
        config_file = "config.txt"

    coin_dict, total = crypt_get(config_file)
    print_folio2(coin_dict, total)

    
