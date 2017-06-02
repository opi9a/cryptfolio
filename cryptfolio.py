from urllib.request import urlretrieve
import json

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
    source = "https://api.coinmarketcap.com/v1/ticker/?convert=GBP&limit=20"
    urlretrieve(source, target)
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

def calc_values(coins):  
    values, total = [], 0.0
    for i,coin in enumerate(coins):
        value=vols[i]*float(prices[i])
        values.append(value)
        total = total + value    
    return values, total

def calc_shares(coins):
    shares = []    
    for i,value in enumerate(values):
        shares.append(value/total)
    return shares

#def get_total_mkt():
#    targeturl = "https://api.coinmarketcap.com/v1/global/?convert=GBP"
#    with urllib.request.urlopen(targeturl) as response:
#        raw_data = response.read()
#
#    # that gives a bytes array, which needs to be converted to a string 
#    # before using json.loads on it
#
#    string = raw_data.decode("utf-8")
#    data = json.loads(string)
#       
#    return data["total_market_cap_gbp"]
#
#def get_coin_caps(coins, datafile):
#    caps = []
#    for coin in coins:
#        for entry in datafile:
#            if entry['id'] == coin:
#                prices.append(float(entry['market_cap_gbp']))
#    return caps    
#
#def calc_total_shares(caps, total_cap):
#    total_shares = []
#    for cap in caps:
#        total_shares.append(cap/total_cap)
#    return total_shares
#

def print_folio(coins, vols, prices, values, shares, total):
        
    len1 = len(max(coins, key=len))
    len2 = len(str(int(max(vols))))
    len3 = len(str(int(max(prices))))
    len4 = len(str(int(max(values))))
    pad = 2
    
# TO DO:  better padding etc
    print("\nCOIN", " "*(len1+1), "PRICE        UNITS        VALUE       SHARE      SHARE OF TOTAL")
    
    for i, coin in enumerate(coins):
        print(coin, end = (" "*(len1+pad-len(coin))))
        print("{:10,.3f}".format(prices[i]), " ",
              "{:10,.2f}".format(vols[i]), " ",
              "{:10,.0f}".format(values[i]),
              "{:10,.1f}%".format(shares[i]*100))
    
    print("\nTOTAL", " "*37, "{:10,.0f}".format(total))
    print("(non", coins[0], " "*30,  "{:10,.0f})".format(total-values[0]))
    print("")




if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        config_file = sys.argv[1]
    else:
        config_file = "config.txt"
    coins, vols = get_coins(config_file)
    prices = get_prices(coins, get_data())
    values, total = calc_values(coins)
    shares = calc_shares(coins)
#    caps = get_coin_caps(coins, get_data())
#    total_cap = get_total_mkt()
#    total_shares = calc_total_shares(caps, total_cap)
    print_folio(coins, vols, prices, values, shares, total)
    
    
