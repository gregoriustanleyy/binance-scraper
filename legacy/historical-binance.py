import pandas as pd
from binance.client import Client
import datetime as dt

# client configuration
api_key = 'KVcT086rW4f2BM9or3bE4cgqC11MnvvKxQryeKx0n3HmkTfBGQwWAlVkcu1evttb' 
api_secret = '1goM6odH4ZQOXe5anVnFy5AD6HlXF8jfoeNUNWfNJbQo4dClyesAOdTmQstREh3w'
client = Client(api_key, api_secret)

symbol = "APTUSDT"
interval = "5m"
Client.KLINE_INTERVAL_5MINUTE 
klines = client.get_historical_klines(symbol, interval, "1 Jan,2021")
data = pd.DataFrame(klines)
 # create colums name
data.columns = ['open_time','open', 'high', 'low', 
                'close', 'volume','close_time', 'qav',
                'num_trades','taker_base_vol','taker_quote_vol', 'ignore']
            
# change the timestamp
data.index = [dt.datetime.fromtimestamp(x/1000.0) for x in data.close_time]
data.to_csv(symbol+'.csv', index = None, header=True)
#convert data to float and plot
df=data.astype(float)
df["close"].plot(title = 'DOTUSDT', legend = 'close')