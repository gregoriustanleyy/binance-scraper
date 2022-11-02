from binance.client import Client
import numpy as np
import requests
import json
import pandas as pd
import datetime as dt


#get token individual data
def get_token_data(symbol: str, interval: str):
    url = 'https://api.binance.com/api/v3/klines'
    par = {'symbol': symbol, 'interval': interval, 'limit': 1000}
    data = pd.DataFrame(json.loads(requests.get(url, params= par).text))
    data.columns = ['datetime', 'open', 'high', 'low', 'close', 'base_volume','close_time', 'quote_volume', 'num_trades','taker_base_vol', 'taker_quote_vol', 'ignore']
    data.index = [dt.datetime.fromtimestamp(x/1000.0) for x in data.datetime]
    data = data.drop(['datetime', "close_time", 'taker_base_vol', 'taker_quote_vol', "ignore"], axis = 1)
    data=data.astype(float)
    return data
    
#get all spot pairs
def all_usdt_spot_pair():
    BASE_URL = 'https://api.binance.com'
    resp = requests.get(BASE_URL+'/api/v1/ticker/allBookTickers')
    ticker_list = json.loads(resp.content)
    symbols = []
    for ticker in ticker_list:
        if str(ticker['symbol'][-4:])=='USDT':
            symbols.append(ticker['symbol'])
    return symbols

#get all futures pair
def all_usdt_futures_pair():
    client = Client(api_key, api_secret)
    info = client.futures_exchange_info()
    temp = [i.get("symbol")[:-4] for i in info.get("symbols")]
    temp.remove("BTCUSDT_22")
    temp.remove("ETHUSDT_22")
    symbols = [str(i + "USDT") for i in set(temp)]
    return symbols

#calculate volatility
def volatility(df: pd.DataFrame):
    df["pct_oc"] = (df["close"] - df["open"])/df["close"]
    df["pct_hl"] = (df["high"] - df["low"])/df["close"]
    df["mean"] = df[["open", "high", "low", "close"]].mean(axis = 1)
    df["vwap"] = (np.cumsum(df["mean"] * df["quote_volume"]) / np.cumsum(df["quote_volume"]))
    df["std"] = df[["open", "high", "low", "close"]].std(axis = 1)
    
    #TODO: find the best way to calculate
    print(df)
    return df["std"].std()/np.sqrt(len(df)), df["pct_oc"].std(), df["pct_hl"].std()

#main function
api_key = 'KVcT086rW4f2BM9or3bE4cgqC11MnvvKxQryeKx0n3HmkTfBGQwWAlVkcu1evttb' 
api_secret = '1goM6odH4ZQOXe5anVnFy5AD6HlXF8jfoeNUNWfNJbQo4dClyesAOdTmQstREh3w'
interval = ['1s', '1m', '5m', '15m', '1h', '1d']
print(volatility(get_token_data("BTCUSDT", "1m")))