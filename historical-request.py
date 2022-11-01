import requests
import json
import pandas as pd
import datetime as dt

url = 'https://api.binance.com/api/v3/klines'
symbol = 'BTCUSDT'
interval = '1d'
par = {'symbol': symbol, 'interval': interval, 'limit': 1001}
data = pd.DataFrame(json.loads(requests.get(url, params= par).text))
#format columns name
data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume','close_time', 'qav', 'num_trades','taker_base_vol', 'taker_quote_vol', 'ignore']
data.index = [dt.datetime.fromtimestamp(x/1000.0) for x in data.datetime]
data=data.astype(float)
# print(start,end)
print(data.tail())
print(data.shape)
print(data['qav'].iloc[0], data['volume'].iloc[0])