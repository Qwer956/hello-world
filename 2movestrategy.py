import ast
from urllib.request import urlopen
import time

tickerall = "https://api.binance.com/api/v1/ticker/price"
tickerallv3 = "https://api.binance.com/api/v3/ticker/price"
exchangeinfo = "https://api.binance.com/api/v3/exchangeInfo"

#get prices function
def getprices(pairlist, url):
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    newticker = html.split("},{")
    
    newprices = []
    
    for p in pairlist:
        pbr = str('"' + p + '"')
        for i in newticker:
            if pbr in i:
                newtickerrev = newticker[::-1]
                if newticker.index(i) == 0:
                    i = i[1:]
                    i = i + "}"
                elif newtickerrev.index(i) == 0:
                    i = i[:-1]
                    i = "{" + i
                else:
                    i = "{" + i + "}"
                i = str(i)
                a = ast.literal_eval(i)
                price = float(a["price"])
                newprices.append(price)
                break
    return newprices

ibal = 100.0

ballist = []

for repeat in range(1000):
    page = urlopen(tickerall)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    ticker = html.split("},{")

    page = urlopen(exchangeinfo)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    exinfo = html[407:]
    exinfo = exinfo.split("]},")

    pairs = []
    prices = []

    #get all pairs and prices 1st time
    for i in ticker:
        if "USDT" in i:
            tickerrev = ticker[::-1]
            if ticker.index(i) == 0:
                i = i[1:]
                i = i + "}"
            elif ticker.index(i) == 0:
                i = i[:-1]
                i = "{" + i
            else:
                i = "{" + i + "}"
            i = str(i)
            a = ast.literal_eval(i)
            pair = a["symbol"]
            bracketpair = str('"' + pair + '"')
            for e in exinfo:
                if bracketpair in e:
                    pos = e.index("isMarginTradingAllowed")
                    margin = (e[pos+24:pos+28])
                    if margin == "true":
                        pairs.append(pair)
                        price = float(a["price"])
                        prices.append(price)
                        break

    #wait 5 mins
    time.sleep(300)

    prices2 = getprices(pairs, tickerall)
    
    difflist = []

    #calculate price difference
    for pos in range(len(pairs)):
        diff = (float(prices2[pos])/float(prices[pos]))
        diff = round(diff, 4)
        difflist.append(diff)

    #wait 5 mins
    time.sleep(300)


    prices3 = getprices(pairs, tickerallv3)

    difflist2 = []

    #calculate 2nd price difference
    for pos in range(len(pairs)):
        diff2 = (prices3[pos] / prices2[pos])
        diff2 = round(diff, 4)
        difflist2.append(diff)

    pairs2row = []
    tdifflist = []

    for i in pairs:
        pos = pairs.index(i)
        if difflist[pos] < 1 and difflist2[pos] < 1 or difflist[pos] > 1 and difflist2[pos] > 1:
            pairs2row.append(i)
            tdiff = round(prices3[pos] / prices[pos], 4)
            tdifflist.append(tdiff)


    abslist = []

    for i in tdifflist:
        if i < 1:
            abs = 1 - i
        else:
            abs = i - 1
        abs = round(abs, 4)
        abslist.append(abs)

    if abslist == []:
        continue
    first = str(pairs[abslist.index(max(abslist))])
    firstpos = abslist.index(max(abslist))
    firstdiff = difflist[firstpos]

#-----------------------------------------



    url = "https://api.binance.com/api/v1/ticker/price?symbol=" + str(first)
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    trade = str(html)
    dict = ast.literal_eval(trade)
    price = float(dict["price"])

    lev = 25
    margin = ibal * lev
    count = margin / price

    time.sleep(600)

    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    trade = str(html)
    dict = ast.literal_eval(trade)
    price2 = dict["price"]
    price2 = float(price2)

    if firstdiff >= 1:
        fbal = ibal + (count * price2) - margin
    else: 
        fbal = ibal + margin - (count * price2)

    fbal = round(fbal,2)
    a = fbal / ibal
    if a < 1:
        a = ((1-a)*100)
        a = "DOWN " + str(round(a, 2))
    else:
        a = ((a-1)*100)
        a = "UP " + str(round(a, 2))

    
    ibal = fbal
    ballist.append(fbal)
    print(ballist)
    if fbal <= 0:
        print("Balance is negative : " + str(fbal))
        break

print("TOTAL FINAL BALANCE : " + str(ibal))
print(ballist)

