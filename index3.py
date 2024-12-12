import ccxt
import matplotlib.pyplot as plt
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

# Initialize the plot
fig, ax = plt.subplots(figsize=(12, 7))
line, = ax.plot(df['timestamp'], df['close'], label='Close Price', color='blue')
live_price_line = ax.axhline(df['close'].iloc[-1], color='red', linestyle='--', label='Live Price')
ax.fill_between(df['timestamp'], df['low'], df['high'], color='gray', alpha=0.3, label='High-Low Range')
ax.set_xlabel('Date')
ax.set_ylabel('Price (USDT)')
ax.legend()
ax.grid()
plt.xticks(rotation=45)
plt.tight_layout()
plt.subplots_adjust(top=0.85)  # Leave more space for the title


# Function to update the chart
def update_chart(frame):
    global df
    # Fetch the live price
    ticker = exchange.fetch_ticker(symbol)
    live_price = ticker['last']

    # Update the live price line
    live_price_line.set_ydata([live_price, live_price])
    
    # Update the title to show the live price
    ax.set_title(f'{symbol} - Last 7 Days (5-Minute Candlestick Chart)\nLive Price: {live_price:.2f} USDT')
    plt.draw()
update_chart(0)
# Use FuncAnimation to call `update_chart` periodically
ani = FuncAnimation(fig, update_chart, interval=5000)  # Update every 5 seconds

plt.show()
