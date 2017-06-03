# AVOID WRITING FILE TO DISK
# It is possible to get prices from the API without writing a file to disk.
# Uses the urlopen method of urllib.request

def get_data_nofile(targeturl):
    import urllib.request
    import json
    
    with urllib.request.urlopen(targeturl) as response:
        raw_data = response.read()

    # that gives a bytes array, which needs to be converted to a string 
    # before using json.loads on it

    string = raw_data.decode("utf-8")
    data = json.loads(string)
    
    return data


# ADD COLORS

def print_color():
    print("\x1b[1;31;40m" + "This is colored" +  "\x1b[0m")


# GET AND SHOW TOTAL MKT CAP

# API call is  https://api.coinmarketcap.com/v1/global/


{
    "total_market_cap_usd": 88439465589.0, 
    "total_24h_volume_usd": 3516436030.0, 
    "bitcoin_percentage_of_market_cap": 45.05, 
    "active_currencies": 740, 
    "active_assets": 119, 
    "active_markets": 3983
}

# REPORT SHARE OF EVENTUAL COINS RELATIVE TO BITCOIN SHARE OF EVENTUAL BITCOINS
# eg if have 0.000010% of eventual bitcoins, and 0.000030% of eventual litecoins
# then this metric is 3.0


def get_total_mkt():
    targeturl = "https://api.coinmarketcap.com/v1/global/?convert=GBP"
    with urllib.request.urlopen(targeturl) as response:
        raw_data = response.read()

#     that gives a bytes array, which needs to be converted to a string 
#     before using json.loads on it

    string = raw_data.decode("utf-8")
    data = json.loads(string)
       
    return data["total_market_cap_gbp"]

def get_coin_caps(coins, datafile):
    caps = []
    for coin in coins:
        for entry in datafile:
            if entry['id'] == coin:
                prices.append(float(entry['market_cap_gbp']))
    return caps    

def calc_total_shares(caps, total_cap):
    total_shares = []
    for cap in caps:
        total_shares.append(cap/total_cap)
    return total_shares


