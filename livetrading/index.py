import backtrader as bt
from backtrader_binance import BinanceStore
import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



cerebro = bt.Cerebro()
# Configure BinanceStore with API keys
binance_store = BinanceStore(
    api_key='',
    api_secret='',
    testnet=False,  # Set to False for live trading
    coin_target='USDT'
)

# Create a data feed for a specific symbol
data = binance_store.getdata(
    dataname='BTCUSDT',  # Pair
    timeframe=bt.TimeFrame.Minutes,
    compression=3,  # 1-minute intervals
    ohlcv_limit=2000,  # Number of candles to fetch
    live=True
)

print(data)
