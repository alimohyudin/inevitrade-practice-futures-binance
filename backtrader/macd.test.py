import unittest
import backtrader as bt
import datetime
from strategy.MACDStrategy import MACDStrategy

# FILE: test_macd_strategy.py


class TestMACDStrategy(unittest.TestCase):

    def setUp(self):
        self.cerebro = bt.Cerebro()
        data = bt.feeds.GenericCSVData(
            dataname='./backtrader/BTCUSDT-3min-3mon.csv',  # Replace with your data file path
            dtformat='%m-%d-%YT%H:%M:%S.000Z',  # New format to match '2024-12-01T00:00:00.000Z'
            timeframe=bt.TimeFrame.Minutes,
            fromdate=datetime.datetime(2024, 10, 1),
            todate=datetime.datetime(2024, 12, 31),
            compression=1,
            openinterest=-1,
        )
        self.cerebro.adddata(data)
        self.cerebro.broker.setcommission(commission=0.0)

    def test_macd_strategy_default_params(self):
        self.cerebro.addstrategy(MACDStrategy)
        self.cerebro.broker.setcash(1000)
        starting_cash = self.cerebro.broker.getvalue()
        self.cerebro.run()
        ending_cash = self.cerebro.broker.getvalue()
        self.assertGreater(ending_cash, starting_cash, "Strategy should result in profit")

    def test_macd_strategy_high_stoploss(self):
        self.cerebro.addstrategy(MACDStrategy, long_stoploss=10, short_stoploss=10)
        self.cerebro.broker.setcash(1000)
        starting_cash = self.cerebro.broker.getvalue()
        self.cerebro.run()
        ending_cash = self.cerebro.broker.getvalue()
        self.assertGreater(ending_cash, starting_cash, "Strategy should result in profit with high stoploss")

    def test_macd_strategy_low_takeprofit(self):
        self.cerebro.addstrategy(MACDStrategy, long_takeprofit=1, short_takeprofit=1)
        self.cerebro.broker.setcash(1000)
        starting_cash = self.cerebro.broker.getvalue()
        self.cerebro.run()
        ending_cash = self.cerebro.broker.getvalue()
        self.assertGreater(ending_cash, starting_cash, "Strategy should result in profit with low takeprofit")

    def test_macd_strategy_custom_rsi(self):
        self.cerebro.addstrategy(MACDStrategy, rsi_period=10, rsi_overbought=80, rsi_oversold=20)
        self.cerebro.broker.setcash(1000)
        starting_cash = self.cerebro.broker.getvalue()
        self.cerebro.run()
        ending_cash = self.cerebro.broker.getvalue()
        self.assertGreater(ending_cash, starting_cash, "Strategy should result in profit with custom RSI settings")

if __name__ == '__main__':
    unittest.main()