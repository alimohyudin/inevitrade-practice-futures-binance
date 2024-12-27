import backtrader as bt
from backtrader_binance_futures import BinanceStore
from ConfigBinance.Config import Config  # Configuration file
import datetime as dt
from strategy.MACDStrategy import MACDStrategy


if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'USDT'  # the base ticker in which calculations will be performed
    symbol = 'BTC' + coin_target  # the ticker by which we will receive data in the format <CodeTickerBaseTicker>

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=Config.TESTNET)  # Binance Storage

    # live connection to Binance - for Offline comment these two lines
    broker = store.getbroker()
    cerebro.setbroker(broker)

    # Historical 1-minute bars for the last hour + new live bars / timeframe M1
    from_date = dt.datetime.now(dt.UTC) - dt.timedelta(hours=48)
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=3, dataname=symbol, start_date=from_date, LiveBars=True)

    cerebro.adddata(data)  # Adding data

    cerebro.addstrategy(MACDStrategy)  # Adding a trading system

    cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart

# import backtrader as bt
# import datetime
# from strategy.MACDStrategy import MACDStrategy

# def run_strategy(params):
#     cerebro = bt.Cerebro()
#     cerebro.addstrategy(MACDStrategy, **params)

#     data = bt.feeds.GenericCSVData(
#         # dataname='./backtrader/data/BTCUSDT-3min-3mon.csv',
#         dataname='./backtrader/data/BTCUSDT-3min-1year-2024.csv',
#         dtformat='%m-%d-%YT%H:%M:%S.000Z',  # New format to match '2024-12-01T00:00:00.000Z'
#         timeframe=bt.TimeFrame.Minutes,
#         fromdate=datetime.datetime(2024, 10, 1),
#         todate=datetime.datetime(2024, 12, 30),
#         compression=1,
#         openinterest=-1,
#     )
#     cerebro.adddata(data)

#     cerebro.broker.setcash(1000)
#     cerebro.broker.setcommission(commission=0.0)

#     starting_cash = cerebro.broker.getvalue()
#     cerebro.run()
#     ending_cash = cerebro.broker.getvalue()

#     profit = ending_cash - starting_cash
#     return profit

# def test_macd_strategy():
#     test_params = [
#         {'long_stoploss': 5, 'long_takeprofit': 3, 'short_stoploss': 2, 'short_takeprofit': 3, 'lookback_bars': 55},
#         # Add more parameter sets as needed
#     ]

#     best_profit = float('-inf')
#     best_params = None

#     for params in test_params:
#         profit = run_strategy(params)
#         print(f"Params: {params}, Profit: {profit}")
#         if profit > best_profit:
#             best_profit = profit
#             best_params = params

#     print(f"Best Params: {best_params}, Best Profit: {best_profit}")

# if __name__ == '__main__':
#     test_macd_strategy()