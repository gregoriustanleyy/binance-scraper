import datetime as dt
import pandas as pd
import json
import requests
import numpy as np
from binance.client import Client
import time
import warnings
warnings.filterwarnings("ignore")
start_time = time.time()
np.set_printoptions(threshold=np.inf)


def to_datetime(timestamp):
    return dt.datetime.fromtimestamp(float(timestamp)/1000.0)

# get token individual data
# cols: datetime, open, high, close, low, volume(usdt), num_trades
def get_token_data(symbol: str, interval: str):
    url = 'https://api.binance.com/api/v3/klines'
    par = {'symbol': symbol, 'interval': interval, 'limit': 1000}
    temp = json.loads(requests.get(url, params=par).text)
    arr = np.delete(np.array(temp), [5, 6, 9 ,10, 11], 1)
    arr[:, 0] = np.array(list(map(to_datetime, arr[:,0])))
    arr[:, 1:6] = arr[:,1:6].astype(float).round(2)
    return arr

#get all SPOT pair
def all_usdt_spot_pair():
    BASE_URL = 'https://api.binance.com'
    resp = requests.get(BASE_URL+'/api/v1/ticker/allBookTickers')
    ticker_list = json.loads(resp.content)
    symbols = [i["symbol"] for i in ticker_list if str(i['symbol'][-4:]) == 'USDT']
    return symbols

# get all FUTURES pair
def all_usdt_futures_pair():
    client = Client(api_key, api_secret)
    info = client.futures_exchange_info()
    temp = [i.get("symbol")[:-4] for i in info.get("symbols")]
    # temp.remove("BTCUSDT_22")
    # temp.remove("ETHUSDT_22")
    symbols = [str(i + "USDT") for i in set(temp)]
    return symbols

# calculate volatility
# cols: datetime, open, high, close, low, volume(usdt), num_trades, pct_oc, pct_hl, avg_price, vwap
def calculate(data: np.ndarray):
    row = np.shape(data)[0]
    open = data[:,1].astype(float)
    high = data[:,2].astype(float)
    close = data[:,3].astype(float)
    low = data[:,4].astype(float)
    vol = data[:,5].astype(float)

    pct_oh = ((close - open) / close * 100).round(2).reshape(row,1)
    pct_hl = ((high - low) / low * 100).round(2).reshape(row,1)
    avg_price = np.mean(data[:,1:5].astype(float), axis = 1).round(2).reshape(row,1)
    vwap = (np.cumsum((high + low + close) / 3 * vol) / np.cumsum(vol)).round(2).reshape(row, 1)
    data = np.concatenate([data, pct_oh, pct_hl, avg_price, vwap], axis=1)

    last_price = float(data[-1,3])
    pct_change = (close[-1] - open[0]) / close[-1] * 100
    avg_trade = np.mean(data[:,6].astype(float))
    avg_vol = np.mean(vol)
    v_t = avg_vol/avg_trade

    vlt = np.round(np.std(vwap/np.mean(vwap))*100, 2)
    # TODO: find the best way to calculate
    # print(np.std(df["close"])/df["close"].mean()*100, np.std(df["avg_price"])/df["avg_price"].mean()*100, )
    return data[0,0], last_price, pct_change, avg_trade, avg_vol, v_t, vlt

# main function
api_key = 'gex1dgknEbsUPpc98goug6xjXdFSOyz8n0GsdA1j15WctlMf57SwQ61yBndP3Wft'
api_secret = 'DtIoYwBlEAD2skWpmvRhZHJO52vJOI7bIqLH1tvp4W2HtlMnIk2c0iQStU1RME9o'
interval = ['1s', '1m', '5m', '15m', '1h']

spot = all_usdt_spot_pair()
futures = all_usdt_futures_pair()
futures_t = "\t".join(futures)
symbols = [i for i in spot if i in futures_t]

final_df = pd.DataFrame(columns=["DateTime", "Token", "TimeFrame", "LastPrice", "% Change",
                        "Avg Num Trade", "Avg Volume", "Volume/Trade", "Volatility"])
count = len(symbols)
for i in symbols:
    count -= 1
    print(str(count) + " Left")
    for j in interval:
        print(i, j)
        run_time = time.time()
        data = get_token_data(symbol=i, interval=j)                                  
        date, last_price, pct_change, avg_trade, avg_vol, v_t, vlt = calculate(data)

        final_df = final_df.append({"DateTime": date, "Token": i, "TimeFrame": j, "LastPrice": last_price, "% Change": pct_change, "Avg Num Trade": avg_trade,
                                   "Avg Volume": avg_vol, "Volume/Trade": v_t, "Volatility": str(str(vlt)+"%")}, ignore_index=True)
        print("--- %s seconds ---" % np.round((time.time() - run_time), 2))  
final_df.to_csv("Volatility.csv")
print("--- %s seconds ---" % np.round((time.time() - start_time), 2))

print(get_token_data("BTCUSDT", "1h"))
