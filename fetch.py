import sqlite3
import urllib.request
import json
import time


sql_create_table = """CREATE TABLE IF NOT EXISTS markets (
    ts integer NOT NULL,
    exchange text NOT NULL,
    symbol text NOT NULL,
    best_bid float NOT NULL,
    best_ask float NOT NULL,
    last float NOT NULL,
    low24 float NOT NULL,
    high24 float NOT NULL,
    base_vol24 float NOT NULL,
    change24 float NOT NULL
);
"""

sql_insert_record = """INSERT INTO markets VALUES (strftime('%s', 'now'), ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

expected_code = "200000"
rtn = urllib.request.urlopen("https://api.kucoin.com/api/v1/market/allTickers").read()
contents = json.loads(rtn)

markets = []

if contents['code'] != expected_code:
    print("Code was %s, expecting %s." % (contents['code'], expected_code))
else:
    data = contents['data']
    t = data['time']
    tickers = data['ticker']
    for ticker in tickers:
        try:
            market = {
                'exchange': 'kucoin',
                'symbol': ticker['symbol'],
                'best_bid': float(ticker['buy']),
                'best_ask': float(ticker['sell']),
                'last': float(ticker['last']),
                'low24': float(ticker['low']),
                'high24': float(ticker['high']),
                'base_vol24': float(ticker['vol']),
                'change24': float(ticker['changeRate']),
            }
            markets.append(market)
        except:
            pass

bittrex_markets = []
bittrex_summaries = {}

rtn = urllib.request.urlopen("https://api.bittrex.com/v3/markets/summaries").read()
summaries = json.loads(rtn)
for entry in summaries:
    change24 = None
    try:
        change24 = entry['percentChange'] 
        market = {
            'low24': float(entry['low']),
            'high24': float(entry['high']),
            'base_vol24': float(entry['volume']),
            'change24': float(change24)
        }
        bittrex_summaries[entry['symbol']] = market
    except:
        pass
       

rtn = urllib.request.urlopen("https://api.bittrex.com/v3/markets/tickers").read()
tickers = json.loads(rtn)
for entry in tickers:
    symbol = entry['symbol']
    try:
        summary = bittrex_summaries[symbol]
        if summary['change24'] is not None:
            market = {
                'exchange': 'bittrex',
                'symbol' : symbol,
                'best_bid': float(entry['bidRate']),
                'best_ask': float(entry['askRate']),
                'last': float(entry['lastTradeRate']),
                'low24': float(summary['low24']),
                'high24': float(summary['high24']),
                'base_vol24': float(summary['base_vol24']),
                'change24': float(summary['change24'])/100,
            }
            markets.append(market)
    except:
        pass

rtn = urllib.request.urlopen("https://poloniex.com/public?command=returnTicker").read()
tickers = json.loads(rtn)
symbols = tickers.keys()

for symbol in symbols:
    entry = tickers[symbol]
    
    market = {
        'exchange': 'poloniex',
        'symbol': symbol,
        'best_bid': float(entry['highestBid']),
        'best_ask': float(entry['lowestAsk']),
        'last': float(entry['last']),
        'low24': float(entry['low24hr']),
        'high24': float(entry['high24hr']),
        'base_vol24': float(entry['baseVolume']),
        'change24': float(entry['percentChange'])/100,
    }
    markets.append(market)

db = sqlite3.connect('market.dat')
cursor = db.cursor()
cursor.execute(sql_create_table)
db.commit()

for entry in markets:
    exchange = entry['exchange']
    symbol = entry['symbol']

    cursor.execute(sql_insert_record,
                (
                    exchange,
                    symbol,
                    entry['best_bid'],
                    entry['best_ask'],
                    entry['last'],
                    entry['low24'],
                    entry['high24'],
                    entry['base_vol24'],
                    entry['change24'],
                ))
    db.commit()
