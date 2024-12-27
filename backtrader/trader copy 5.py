import backtrader as bt
import datetime
from strategy.MACDStrategy import MACDStrategy
import concurrent.futures
import itertools

def run_strategy(params):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MACDStrategy, **params)

    data = bt.feeds.GenericCSVData(
        #dataname='./backtrader/data/BTCUSDT-3min-3mon.csv',
        dataname='./backtrader/data/BTCUSDT-3min-1year-2024.csv',
        dtformat='%m-%d-%YT%H:%M:%S.000Z',  # New format to match '2024-12-01T00:00:00.000Z'
        timeframe=bt.TimeFrame.Minutes,
        fromdate=datetime.datetime(2024, 6, 1),
        todate=datetime.datetime(2024, 7, 1),
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
    return profit, params

def generate_params_grid():
    long_stoploss = [5]
    long_takeprofit = [3]
    short_stoploss = [2]
    short_takeprofit = [3]
    lookback_bars = [55]
    #660$ for 5, 2, 2, 2, 55
    #745$ for 5, 3, 2, 3, 55
    param_grid = list(itertools.product(long_stoploss, long_takeprofit, short_stoploss, short_takeprofit, lookback_bars))
    return [{'long_stoploss': p[0], 'long_takeprofit': p[1], 'short_stoploss': p[2], 'short_takeprofit': p[3], 'lookback_bars': p[4]} for p in param_grid]

def test_macd_strategy():
    test_params = generate_params_grid()

    best_profit = float('-inf')
    best_params = None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_strategy, params) for params in test_params]
        for future in concurrent.futures.as_completed(futures):
            profit, params = future.result()
            print(f"Params: {params}, Profit: {profit}")
            if profit > best_profit:
                best_profit = profit
                best_params = params

    print(f"Best Params: {best_params}, Best Profit: {best_profit}")

if __name__ == '__main__':
    test_macd_strategy()