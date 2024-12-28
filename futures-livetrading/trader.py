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
