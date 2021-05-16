import sqlite3
import time

def sort_handler(e):
    return e[2]

sql_select_pair = """SELECT ts, best_bid, best_ask, last, low24, high24, base_vol24, change24 FROM markets WHERE exchange=? AND symbol=? AND ts >= ? AND ts <= ? ORDER BY ts DESC;"""
sql_select_distinct = """SELECT DISTINCT exchange, symbol FROM markets;"""

t_end = int(time.time())
t_start = t_end - 86400

db = sqlite3.connect('market.dat')
cursor = db.cursor()

cursor.execute(sql_select_distinct)
db.commit()
results = cursor.fetchall()

pairs = []
for entry in results:
    exchange = entry[0]
    symbol = entry[1]
    cursor.execute(sql_select_pair, (exchange, symbol, t_start, t_end,))
    db.commit()
    item = cursor.fetchall()
    first = item[0]
    second = item[1]
    rate = first[7] - second[7]
    pair = (exchange, symbol, rate, item)
    pairs.append(pair)

pairs.sort(key=sort_handler)

for pair in pairs:
    print(pair)
