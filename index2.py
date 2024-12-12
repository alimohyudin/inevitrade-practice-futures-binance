import ccxt
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import time

# Initialize Binance Futures exchange
exchange = ccxt.binance({
    'options': {'defaultType': 'future'},  # For Binance Futures
})

# Define parameters
symbol = 'BTC/USDT'  # Replace with the symbol you want
timeframe = '5m'  # 5-minute candles
since = int((datetime.utcnow() - timedelta(days=7)).timestamp() * 1000)  # 7 days ago

# Fetch OHLCV data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)

# Convert to a Pandas DataFrame for easier manipulation
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Function to fetch live price and update the chart
def update_chart():
    # Fetch live price
    ticker = exchange.fetch_ticker(symbol)
    live_price = ticker['last']
    
    # Plot the candlestick chart
    plt.clf()  # Clear the figure
    plt.plot(df['timestamp'], df['close'], label='Close Price', color='blue')
    plt.fill_between(df['timestamp'], df['low'], df['high'], color='gray', alpha=0.3, label='High-Low Range')

    # Add live price as a horizontal line
    plt.axhline(live_price, color='red', linestyle='--', label=f'Live Price: {live_price:.2f}')

    # Chart details
    plt.title(f'{symbol} - Last 7 Days (5-Minute Candlestick Chart)')
    plt.xlabel('Date')
    plt.ylabel('Price (USDT)')
    plt.legend()
    plt.grid()

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.pause(0.1)  # Pause to allow the figure to update

# Display the chart with periodic updates
plt.figure(figsize=(12, 6))
while True:
    update_chart()
    time.sleep(5)  # Wait for 5 seconds before updating the chart
