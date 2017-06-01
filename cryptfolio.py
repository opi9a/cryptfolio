from urllib.request import urlretrieve
import json

def get_coins(conf="config.txt"):  
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

def get_values(coins):  
    values = []
    total = 0.0
    
    for i,coin in enumerate(coins):
        value=vols[i]*float(prices[i])
        values.append(value)
        total = total + value
    
    return values, total

def get_shares(coins):
    shares = []    
    for i,value in enumerate(values):
        shares.append(value/total)
    
    return shares

def print_folio(coins, vols, prices, values, shares, total):
        
    len1 = len(max(coins, key=len))
    len2 = len(str(int(max(vols))))
    len3 = len(str(int(max(prices))))
    len4 = len(str(int(max(values))))
    pad = 2
    
    print("\nCOIN", " "*(len1+1), "PRICE        UNITS        VALUE       SHARE")
    
    for i, coin in enumerate(coins):
        print(coin, end = (" "*(len1+pad-len(coin))))
        print("{:10,.2f}".format(prices[i]), " ",
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
    values, total = get_values(coins)
    shares = get_shares(coins)
    print_folio(coins, vols, prices, values, shares, total)
    
    
