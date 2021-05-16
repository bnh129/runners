fetch.py reads the following for all trading pairs on poloniex, bittrex, and kucoin, and loads it into a sqlite database.

	bid, ask, last price, 24 hr low, 24 hr high, 24 hr volume, price change over 24 hours

list.py reads from the database and sorts trading pairs based on the rate of price change since the last time fetch.py was run.

So you could run fetch.py every 20 minutes, for example, and get an idea of which pairs have started to run in the last 20 minutes, reported at the bottom of the list.
