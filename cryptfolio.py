from urllib.request import urlretrieve

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

coins, vols = get_coins()
prices = get_prices(coins, get_data())
values = []
total = 0.0

for i,coin in enumerate(coins):
    value=vols[i]*float(prices[i])
    values.append(value)
    total = total + value

print(total)

shares = []    
for i,value in enumerate(values):
    shares.append(value/total)
    
len1 = len(max(coins, key=len))
len2 = len(str(int(max(vols))))
len3 = len(str(int(max(prices))))
len4 = len(str(int(max(values))))

print("")
print("\nCOIN", " "*(len1+1), "PRICE        UNITS        VALUE       SHARE")

for i, coin in enumerate(coins):
    print(coin, end = (" "*(len1+2-len(coin))))
    print("{:10,.2f}".format(prices[i]), " ",
          "{:10,.2f}".format(vols[i]), " ",
          "{:10,.0f}".format(values[i]),
          "{:10,.1f}%".format(shares[i]*100))

print("\nTOTAL", " "*37, "{:10,.0f}".format(total))
