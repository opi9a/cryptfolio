#!/home/gav/anaconda3/python3

# CRYPTOCOMPARE ONLY ACCEPTS 7 COINS

import requests
import json
import datetime
import pandas as pd

def get_basics(conf='config.txt'):
    print('\nin read_config\n')
    out = {}
    out['coins'], out['vols'] = get_coins(conf)
    out['ticks'] = get_tickers(out['coins'])
    return out


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

def get_data(depth=85):
    base="https://api.coinmarketcap.com/v1/ticker/?convert=GBP&limit="
    req = requests.get("".join([base,str(depth)]))
    data = json.loads(req.text)       
    return data

def get_prices(coins, datafile):
    prices = []
    for coin in coins:
        for entry in datafile:
            if entry['id'] == coin:
                prices.append(float(entry['price_gbp']))
    return prices

def get_hist(tickers, timestamp, max_q=7):
    '''Returns a dictionary of coins with 1/price in GBP
    '''
    base = '''https://min-api.cryptocompare.com/data/pricehistorical?fsym=GBP&tsyms='''
    last=0
    out=pd.DataFrame(index=[timestamp])
    while last<len(tickers):
        c_slice = slice(last, 1+min(last+max_q, len(tickers)))
#        print(c_slice)
        ticks=",".join(tickers[c_slice])
        ts="".join(["&ts=", str(timestamp)])
        url = "".join([base, ticks, ts])
#        print(url)
        req = requests.get(url).text
#        print(req)
        out_dict = json.loads(req)['GBP'] 
#        print(out_dict)
        out_df = pd.DataFrame(out_dict,index=[timestamp])
#        print(out_df)
        out=out.join(out_df)
        last += max_q+1 

    return out
        
# def get_tickers(coins):
# 	ticks = []
# 	for c in coins:
# 		req=requests.get("".join(["https://api.coinmarketcap.com/v1/ticker/",c,"/"])).text
# 		tick = json.loads(req)[0]['symbol']
# 		ticks.append(tick)
# 	return ticks

def get_tickers(coins):
    ticks = []
    for c in coins:
        try:
            req=requests.get("".join(["https://api.coinmarketcap.com/v1/ticker/",c,"/"])).text
            tick = json.loads(req)[0]['symbol']
            ticks.append(tick)
        except:
            print("couldn't find a coin called ", c)
    return ticks


def get_multi(ticks):
    base = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms="
    content = ",".join(ticks)
    end = "&tsyms=GBP,USD,BTC"
    api_str = "".join([base, content, end])
    req=requests.get(api_str).text
    mult = json.loads(req)['RAW']
    
    mdf = pd.DataFrame(index=ticks)

    mdf['prices_gbp'] = [mult[t]['GBP']['PRICE'] for t in ticks]
    mdf['prices_usd'] = [mult[t]['USD']['PRICE'] for t in ticks]
    mdf['prices_btc'] = [mult[t]['BTC']['PRICE'] for t in ticks]
    mdf['cap_gbp'] = [mult[t]['GBP']['MKTCAP'] for t in ticks]
    mdf['cap_usd'] = [mult[t]['USD']['MKTCAP'] for t in ticks]
    mdf['ch24h_gbp'] = [mult[t]['GBP']['CHANGE24HOUR'] for t in ticks]
    mdf['ch24h_usd'] = [mult[t]['USD']['CHANGE24HOUR'] for t in ticks]
    
    return mdf

def get_now_prices(ticks):
    base = "https://min-api.cryptocompare.com/data/price?fsym=GBP&tsyms="
    req=requests.get("".join([base,",".join(ticks)])).text
    return(1/pd.DataFrame(json.loads(req),index=['prices']))

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


def make_df(basics):
    '''Takes input of a `basics` dict - output of `get_basics()`,
    which has structure {'coins':[], 'ticks':[], 'vols':[]}

    Uses this to generate a dataframe with all relevant info, 
    generated by call to `get_multi()`.

    Returns a dataframe.

    '''
    
    df=pd.DataFrame(basics).set_index('coins')

    df=df.join(get_multi(list(df['ticks'])),on='ticks')
    df['pcent_24h_ch']=df['ch24h_gbp']/(df['ch24h_gbp']+df['prices_gbp'])
    df['values']=df['prices_gbp']*df['vols']
    total = sum(df['values'])

    df['values_btc']=df['prices_btc']*df['vols']

    df['value_24h_ch']=df['ch24h_gbp']*df['vols']
    df['val_pcent_24h_ch']=df['value_24h_ch']/(df['value_24h_ch']+df['values'])

    total_ch = sum(df['value_24h_ch'])
    total_perc_ch = total_ch/(total_ch+total)

    df['shares']=df['values']/total

    btc_proportion=df.loc['bitcoin','values']/df.loc['bitcoin','cap_gbp']
    df['weight']=((df['values']/df['cap_gbp'])/btc_proportion)
    df['£PPPW']=btc_proportion*df['cap_gbp']*0.01

    return df


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
    req=requests.get('https://blockchain.info/q/getblockcount').text
    h = json.loads(req)
    return h


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        config_file = sys.argv[1]
    else:
        config_file = "config.txt"

    coin_dict, total = crypt_get(config_file)
    print_folio2(coin_dict, total)

    
