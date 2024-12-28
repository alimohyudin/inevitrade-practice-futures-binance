import backtrader as bt
import datetime
from strategy.MACDStrategy import MACDStrategy
from fetch_data import fetch_1year_data

# Fetch 1 year of data
fetch_1year_data('BTCUSDT')

cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(
    dataname='./data/BTCUSDT.csv',  # Replace with your data file path
    dtformat='%m-%d-%YT%H:%M:%S.000Z',  # New format to match '2024-12-01T00:00:00.000Z'
    timeframe=bt.TimeFrame.Minutes,
    fromdate=datetime.datetime(2024, 12, 16),
    todate=datetime.datetime(2024, 12, 31),
    compression=3,
    openinterest=-1,
)
print(len(data))
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(MACDStrategy, lookback_bars=55)

# Run
cerebro.broker.setcash(1000)
cerebro.broker.setcommission(commission=0.0)
print(f'Starting Portfolio Value: {cerebro.broker.getvalue()}')
cerebro.run()
print(f'Final Portfolio Value: {cerebro.broker.getvalue()}')
cerebro.plot()