import ccxt
import mplfinance as mpf
import pandas as pd
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation

# Initialize Binance Futures exchange
exchange = ccxt.binance({
    'options': {'defaultType': 'future'},  # For Binance Futures
})

# Define parameters
symbol = 'BTC/USDT'  # Replace with the symbol you want
timeframe = '5m'  # 5-minute candles
since = int((datetime.utcnow() - timedelta(days=1)).timestamp() * 1000)  # 7 days ago

# Fetch OHLCV data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)

# Convert to a Pandas DataFrame for easier manipulation
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Initialize the candlestick plot
fig, axes = mpf.plot(
    df,
    type='candle',  # Candlestick chart
    style='binance',
    title=f"{symbol} - Last 7 Days (5-Minute Candlestick Chart)",
    ylabel='Price (USDT)',
    returnfig=True
)

# Access the first axis in the list of axes
ax = axes[0]

# Function to update the candlestick chart and live price
def update_chart(frame):
    global df

    # Fetch live price
    ticker = exchange.fetch_ticker(symbol)
    live_price = ticker['last']

    # Update the chart title with live price
    #ax.set_title(f"{symbol} - Last 7 Days (5-Minute Candlestick Chart)\nLive Price: {live_price:.2f} USDT")

    # Optionally fetch the latest OHLCV data
    latest_ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=1)
    latest_df = pd.DataFrame(latest_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    latest_df['timestamp'] = pd.to_datetime(latest_df['timestamp'], unit='ms')
    latest_df.set_index('timestamp', inplace=True)

    # Append or update the latest candle in the DataFrame
    df.update(latest_df)

    # Clear and replot with the updated data
    ax.clear()
    ax.set_title(f"Live Price: {live_price:.2f} USDT")
    mpf.plot(
        df,
        type='candle',
        style='binance',
        ax=ax,
        ylabel='Price (USDT)'
    )

# Use FuncAnimation to periodically update the chart
ani = FuncAnimation(fig, update_chart, interval=5000, cache_frame_data=False)  # Update every 5 seconds

mpf.show()
