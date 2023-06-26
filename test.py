import ccxt

def fetch_usdm_future_symbols():
    binance = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'future'},
    })

    markets = binance.fapiPublicGetExchangeInfo()['symbols']
    usdm_futures_symbols = [
        market['symbol'] 
        for market in markets
        if market['contractType'] == 'PERPETUAL'
    ]

    return usdm_futures_symbols

symbols = fetch_usdm_future_symbols()
print(symbols)
