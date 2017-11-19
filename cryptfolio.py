#!/home/gav/anaconda3/python3

# CRYPTOCOMPARE ONLY ACCEPTS 7 COINS

import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import sys

def get_basics(conf='config.txt'):
    '''Reads in the config file.

    Returns a dictionary with coins, vols and ticks as lists.
    '''

    out = dict(coins=[], vols=[], ticks=[])

    with open(conf, "r") as f:
        rows = [(l.split()[0], float(l.split()[1])) for l in f if l[0]!='#']

    out['coins'] = [x[0] for x in rows]
    out['vols'] = [x[1] for x in rows]

    for coin in out['coins']:
        try:
            req=requests.get("".join(["https://api.coinmarketcap.com/v1/ticker/",coin,"/"])).text
            tick = json.loads(req)[0]['symbol']
            out['ticks'].append(tick)
        except:
            print("couldn't find a coin called ", coin)

    return out


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


def get_hist(tickers, timestamp, max_q=6, _debug=False):
    '''Returns a dictionary of coins with 1/price in GBP
    '''
    base = '''https://min-api.cryptocompare.com/data/pricehistorical?fsym=GBP&tsyms='''
    last=0
    row = pd.datetime.fromtimestamp(timestamp).date()
    out=pd.DataFrame(index=[row])

    if _debug: print("getting ", row, "...", end="  ")

    while last<len(tickers):
        c_slice = slice(last, 1+min(last+max_q, len(tickers)))
        ticks=",".join(tickers[c_slice])
        ts="".join(["&ts=", str(timestamp)])

        url = "".join([base, ticks, ts])

        req = requests.get(url).text
        out_dict = json.loads(req)['GBP'] 
        out_df = pd.DataFrame(out_dict,index=[row])
        out=out.join(out_df)
        last += max_q+1 
    
    if _debug: print("ok")

    return out
        

def fill_history(df, _debug=False):
    '''Extends an input dataframe with prices, by working out list of days to get,
    and calling get_hist() function to do the scraping.
    '''
    pad = 20
    
    # find last date in input dataframe
    first_missing_date = df.index[-1] + timedelta(days=1)
    if _debug: print("first_missing_date: ".ljust(pad), first_missing_date)

    # find yesterday - don't want today
    yday = pd.to_datetime(datetime.now() - timedelta(days=1)).date()
    if _debug: print("yesterday is: ".ljust(pad), yday)
        
    # get list of missing dates
    date_range = pd.date_range(first_missing_date, yday)
    if _debug: print("number of days missing ".ljust(pad), len(date_range))
    missing_days = [x.timestamp() for x in date_range]

    # retrieve prices for list of missing dates
    for d in missing_days:
        try:
            new_row = 1/get_hist(list(df.columns), d, _debug=_debug)
            new_row[new_row==np.inf]=0
            df=df.append(new_row)
        except:
            print("failed")
            return df
    return df


def plot_history(basics, interactive = False):
    # load past prices and fill
    price_hist = fill_history(pd.read_pickle("price_history.pkl"))

    # save (before adding today's prices)
    price_hist.to_pickle("price_history.pkl")
    price_hist.to_csv("price_history.csv")

    # append today's prices
    today_row = pd.DataFrame([get_now_prices(price_hist.columns).loc['prices', x] for x in price_hist.columns], 
                 index=price_hist.columns, columns=[pd.to_datetime(datetime.now().date())]).T

    price_hist1 = price_hist.append(today_row)

    # make value history
    value_hist = pd.concat([price_hist1[tick]*basics['vols'][i] for i, tick in enumerate(basics['ticks'])], axis=1)
    sum_hist = value_hist.sum(axis=1)

    if interactive:
        from bokeh.plotting import figure, show, ColumnDataSource
        from bokeh.models import NumeralTickFormatter, Range1d, DataRange1d, HoverTool
        from bokeh.embed import components

        df = pd.DataFrame(sum_hist, columns=["value"])
        df['dates'] = sum_hist.index

        source = ColumnDataSource(df)
        source.add(df['dates'].apply(lambda x: x.strftime("%d %b %y")), name='t_dates')
        hover = HoverTool(tooltips=[
            ("date","@t_dates"),
            ("value","£$y{int,}"),
        ])

        TOOLS = "pan,wheel_zoom,box_zoom,xzoom_in,xzoom_out,yzoom_in,yzoom_out,reset,save,box_select,undo, redo"

        p = figure(title="Portfolio value", y_axis_label='£',
                   plot_width=1000, plot_height=550,
                   tools=[hover, TOOLS], logo="grey",
                  x_axis_type="datetime")

        p.line(x='dates', y='value', source=source, line_width=2)
        p.yaxis[0].formatter = NumeralTickFormatter(format="£0,")
        p.y_range = Range1d(bounds=(0, max(sum_hist)*1.1))
        p.y_range = DataRange1d(bounds=(0, max(sum_hist)*1.1))

        script, div = components(p)

        return script, div


    else:
        yr_ago = pd.to_datetime(datetime.now() - timedelta(days=365)).date()
        month_ago = pd.to_datetime(datetime.now() - timedelta(days=30)).date()

        fig, axs = plt.subplots(1,3, figsize = (20,10), sharey=True)
        axs[0].plot(sum_hist)
        axs[0].set_title("All Time")
        axs[1].plot(sum_hist.loc[yr_ago:])
        axs[1].set_title("1 Year")
        axs[2].plot(sum_hist.loc[month_ago:])
        axs[2].set_title("1 Month")

        plotfile = "".join(["static/figs/testfig_", str(int(datetime.now().timestamp())),".png"])

        print("plotfile is ", plotfile)

        fig.savefig(plotfile)

        return plotfile


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
    print(str(datetime.now()).split(".")[0])
    
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
    basics = get_basics(config_file)
    coins = basics['coins']
    vols = basics['vols']
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

    
