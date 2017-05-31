from urllib.request import urlretrieve

coins = []
vols = []

with open("config.txt", "r") as f:
    i = 0
    for line in f:
        if line[0] != "#":
            coins.append(line.split()[0])
            vols.append(line.split()[1])
           # coins[i],vols[i] = line.split(",")
            i+=1

maxlen = len(max(coins, key=len))

dest = "request.txt"

print("\nCOIN          PRICE        UNITS       VALUE")

count = 0
total, btcsum = 0,0
for coin in coins:
    target = "https://api.coinmarketcap.com/v1/ticker/" + coin + "/?convert=GBP"
    urlretrieve(target, dest)
    with open(dest, "r") as f:
        for line in f:
            if "price_gbp" in line:
                price = float(line.split(": ")[1].split("\"")[1])
                coinstring = coin + " "*(maxlen-len(coin))
                value = float(vols[count])*price
                print(coinstring+ " {:10,.2f}".format(price), end="   ")
                print("{:10,.2f}".format(float(vols[count])), end = "  ")
                print("{:10,.2f}".format(value))
                total = total + value
    if coin == "bitcoin":
        btcsum = value
    count+=1

print("\nTOTAL                             {:10,.0f}".format(total))
print("(non bitcoin                      {:10,.0f})".format(total-btcsum))

print("")
