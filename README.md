# cryptfolio

Very basic python 3.x tool for collecting crypto prices from www.coinmarketcap.com and printing portfolio values in GBP.

Usage:  
    `python3 cryptfolio.py [OPTIONAL config file name - defaults to config.txt]`

Looks by for config file in the same folder containing currency names and volumes (number of units of the currency) separated by a space.  Then queries www.coinmarketcap.com for the prices, and calculates the values etc (currently limited to searching the top 20 currencies).

For example, running `python3 cryptfolio.py` in a folder with a `config.txt` file containing the following:

    # comments can go here
    bitcoin 1.337
    dogecoin 99999.99
    monero 12.34

will return

    COIN           PRICE        UNITS        VALUE       SHARE
    bitcoin     1,837.94         1.34        2,457       79.4%
    dogecoin        0.00    99,999.99          214        6.9%
    monero         34.32        12.34          424       13.7%

    TOTAL                                            3,095
    (non bitcoin                                       637)

Lines in the config file beginning `#` will be ignored.  It fails if lines are empty.

Can optionally pass a config file by name in the command line, or it will default to look for `config.txt`.

Check http://coinmarketcap.com/api/ for the API, or https://api.coinmarketcap.com/v1/ticker/limit=20 to work out naming conventions (returns all data).
