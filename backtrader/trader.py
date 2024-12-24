import backtrader as bt

class MACDStrategy(bt.Strategy):
    params = (
        ('enable_long_strategy', True),
        ('long_stoploss', 0.05),
        ('long_takeprofit', 0.02),
        ('enable_short_strategy', True),
        ('short_stoploss', 0.04),
        ('short_takeprofit', 0.04),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('ema_periods', [9, 21, 50, 100, 200]),
        ('start_date', None),
        ('end_date', None),
    )

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):
        # Indicators
        self.rsi = bt.indicators.RSI_Safe(self.data.close, period=self.params.rsi_period)
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal,
        )

        self.ema_lines = [bt.indicators.EMA(self.data.close, period=period) for period in self.params.ema_periods]

         # Custom counters for `barssince`
        self.bars_since_oversold = None
        self.bars_since_overbought = None

    def next(self):
        # Date range filtering
        # if self.params.start_date and self.params.end_date:
        #     if not (self.params.start_date <= self.datetime.date() <= self.params.end_date):
        #         return
        self.log(f'Close: {self.data.close[0]}')
        
        # Update `barssince` counters
        if self.rsi[0] <= self.params.rsi_oversold:
            self.bars_since_oversold = 0  # Reset counter
        elif self.bars_since_oversold is not None:
            self.bars_since_oversold += 1

        if self.rsi[0] >= self.params.rsi_overbought:
            self.bars_since_overbought = 0  # Reset counter
        elif self.bars_since_overbought is not None:
            self.bars_since_overbought += 1

        # Generate signals
        was_oversold = self.bars_since_oversold is not None and self.bars_since_oversold <= 10
        was_overbought = self.bars_since_overbought is not None and self.bars_since_overbought <= 10
        crossover_bull = self.macd.macd[0] > self.macd.signal[0]
        crossover_bear = self.macd.macd[0] < self.macd.signal[0]

        self.buy_signal = was_oversold and crossover_bull
        self.sell_signal = was_overbought and crossover_bear

        

        # self.buy()
        # self.sell()
        # Long Strategy
        if self.buy_signal and self.params.enable_long_strategy:
            print("was_oversold=", self.rsi[0], self.params.rsi_oversold, was_oversold)
            self.close_short()
            if not self.position:
                print("buy")
                self.buy()

        # Short Strategy
        if self.sell_signal and self.params.enable_short_strategy:
            print("was_overbought=", self.rsi[0], self.params.rsi_overbought, was_overbought)
            self.close_long()
            if not self.position:
                print("sell")
                self.sell()

    def close_long(self):
        if self.position.size > 0:
            self.close()

    def close_short(self):
        if self.position.size < 0:
            self.close()

# Data preparation
cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(
    dataname='./backtrader/BTCUSDT.csv',  # Replace with your data file path
    dtformat='%m-%d-%YT%H:%M:%S.000Z',  # New format to match '2024-12-01T00:00:00.000Z'
    timeframe=bt.TimeFrame.Minutes,
    compression=1,
    openinterest=-1,
)
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(MACDStrategy)

# Run
cerebro.broker.setcash(200.0)
cerebro.broker.setcommission(commission=0.0)
print(f'Starting Portfolio Value: {cerebro.broker.getvalue()}')
cerebro.run()
print(f'Ending Portfolio Value: {cerebro.broker.getvalue()}')

# Visualization
cerebro.plot()
