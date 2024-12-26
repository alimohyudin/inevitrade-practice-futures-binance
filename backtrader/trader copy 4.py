import backtrader as bt
import datetime
from strategy.MACDStrategy import MACDStrategy

def run_strategy(params):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MACDStrategy, **params)

    data = bt.feeds.GenericCSVData(
        dataname='./backtrader/BTCUSDT-3min-3mon.csv',  # Replace with your data file path
        dtformat='%m-%d-%YT%H:%M:%S.000Z',  # New format to match '2024-12-01T00:00:00.000Z'
        timeframe=bt.TimeFrame.Minutes,
        fromdate=datetime.datetime(2024, 10, 1),
        todate=datetime.datetime(2024, 12, 31),
        compression=1,
        openinterest=-1,
    )
    cerebro.adddata(data)

    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.0)

    starting_cash = cerebro.broker.getvalue()
    cerebro.run()
    ending_cash = cerebro.broker.getvalue()

    profit = ending_cash - starting_cash
    return profit

def test_macd_strategy():
    test_params = [
        {'lookback_bars': 10},
        {'lookback_bars': 15},
        {'lookback_bars': 20},
        {'lookback_bars': 25},
        {'lookback_bars': 30},
        {'lookback_bars': 35},
        {'lookback_bars': 40},
        {'lookback_bars': 45},
        {'lookback_bars': 50},
        {'lookback_bars': 55},
        {'lookback_bars': 60}
        # Add more parameter sets as needed
    ]

    best_profit = float('-inf')
    best_params = None

    for params in test_params:
        profit = run_strategy(params)
        print(f"Params: {params}, Profit: {profit}")
        if profit > best_profit:
            best_profit = profit
            best_params = params

    print(f"Best Params: {best_params}, Best Profit: {best_profit}")

if __name__ == '__main__':
    test_macd_strategy()