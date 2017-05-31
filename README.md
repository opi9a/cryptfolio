# cryptfolio

Very basic and not very efficient python 3.x tool for collecting crypto prices from www.coinmarketcap.com and printing portfolio values in GBP.

Looks for a `config.txt` file in the same folder, with currency names and volumes separated by a space, eg a `config.txt` file containing:

    bitcoin 1.337
    dogecoin 99999.99
    monero 12.34

will return

    COIN          PRICE        UNITS       VALUE
    bitcoin    1,778.79         1.34    2,378.25
    dogecoin       0.00    99,999.99      209.99
    monero        32.63        12.34      402.71

    TOTAL                                  2,991
    (non bitcoin                             613)


Lines beginning `#` will be ignored.  It fails if lines are empty.

Check http://coinmarketcap.com/api/ for the API, or https://api.coinmarketcap.com/v1/ticker/ to work out naming conventions (returns all data).
