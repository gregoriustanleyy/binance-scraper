import requests
from time import sleep
import ccxt
import time
import pandas as pd
import numpy as np
import concurrent.futures
from tqdm import tqdm
import traceback

def fetch_usdm_future_symbols(binance):
    markets = binance.fapiPublicGetExchangeInfo()['symbols']
    usdm_futures_symbols = [
        market['symbol'] 
        for market in markets
        if market['contractType'] == 'PERPETUAL'
    ]

    return usdm_futures_symbols

# Functions for sending messages and getting updates from Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, params=params)
    return response.json()

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(url, params=params)
    return response.json()

def main_function(chat_id):
    start = time.time()

    def rogers_satchell_volatility(high, low, open, close):
        ln_hl = np.log(high / low)
        ln_co = np.log(close / open)
        rs = ln_hl * (ln_hl - ln_co)
        return np.sqrt(np.mean(rs))

    def average_true_range(high, low, close, period=14):
        hl = high - low
        hc = np.abs(high - close.shift())
        lc = np.abs(low - close.shift())
        tr = np.maximum(np.maximum(hl, hc), lc)
        atr = tr.rolling(window=period).mean()
        return atr

    def fetch_token_data(symbol):
        try:
            ohlcv = binance.fetch_ohlcv(symbol, '1h', limit=500)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['token'] = symbol
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['price'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            df['frequency'] = '1h'
            df['volatility'] = df[['high', 'low', 'open', 'close']].astype(float).apply(
                lambda x: rogers_satchell_volatility(x['high'], x['low'], x['open'], x['close']), axis=1)
            df['ATR'] = average_true_range(df['high'].astype(float), df['low'].astype(float), df['close'].astype(float))
            df['VWAP'] = (df['volume'] * (df['high'].astype(float) + df['low'].astype(float) + df['close'].astype(float)) / 3).cumsum() / df['volume'].cumsum()
            df['action'] = np.where(df['price'] > df['VWAP'], 'SELL', 'BUY')

            latest_volatility = df['volatility'].iloc[-1]
            latest_ATR = df['ATR'].iloc[-1]
            latest_action = df['action'].iloc[-1]

            return symbol, {'volatility': latest_volatility, 'ATR': latest_ATR, 'action': latest_action}
        except Exception as e:
            return symbol, None

    binance = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'future'},
    })

    symbols = fetch_usdm_future_symbols(binance)

    token_data = {}
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(fetch_token_data, symbols), total=len(symbols)))

    for result in results:
        symbol, data = result
        if data is not None:
            token_data[symbol] = data

    sorted_by_volatility = sorted(token_data.items(), key=lambda x: x[1]['volatility'], reverse=True)
    sorted_by_ATR = sorted(token_data.items(), key=lambda x: x[1]['ATR'], reverse=True)

    message = "Top 3 most volatile tokens:\n"
    for i in range(min(3, len(sorted_by_volatility))):
        token, data = sorted_by_volatility[i]
        message += f"{token} Volatility: {data['volatility']:.5f} ATR: {data['ATR']:.5f} Action: {data['action']}\n"

    message += "\nTop 3 tokens with the highest ATR:\n"
    for i in range(min(3, len(sorted_by_ATR))):
        token, data = sorted_by_ATR[i]
        message += f"{token} Volatility: {data['volatility']:.5f} ATR: {data['ATR']:.5f} Action: {data['action']}\n"

    message += f"\nProgram runtime: {time.time() - start:.2f} seconds"
    
    send_message(chat_id, message)

# Function to run the main function on a trigger message
def run_script_on_trigger(bot_token, trigger_message):
    update_id = None
    while True:
        try:
            updates = get_updates(update_id)
            for update in updates['result']:
                message_text = update['message']['text']
                chat_id = update['message']['chat']['id']
                if message_text == trigger_message:
                    main_function(chat_id)
                update_id = update['update_id'] + 1
        except Exception as e:
            error_message = f"Error occurred:\n{traceback.format_exc()}"
            send_message(default_chat_id, error_message)
            continue
        sleep(1)

# Set your bot token and trigger message
bot_token = "6119013820:AAEqWzgHH4qnideh3hs9Mug3iGEzSYKZZ3k"
trigger_message = "fetch binance dat"
default_chat_id = 920877069

run_script_on_trigger(bot_token, trigger_message)
