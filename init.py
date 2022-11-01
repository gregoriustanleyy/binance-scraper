import binance
import pandas as pd

client = binance.Client()

r = client.futures_continous_klines(
    pair='APTUSDT',
    contractType='PERPETUAL',
    interval='5m',
)
df = pd.DataFrame(r)
df = df[[0,1,4,5,8]]
print(df)