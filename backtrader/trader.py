import backtrader as bt
import datetime

total_closed_positions = 0
a_calculated_profit = 0
a_max_trades = 999
a_position_closed = True

class MACDStrategy(bt.Strategy):
    params = (
        ('enable_long_strategy', True),
        ('long_stoploss', 5),#percent
        ('long_takeprofit', 2),
        ('enable_short_strategy', True),
        ('short_stoploss', 4),
        ('short_takeprofit', 4),
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('ema_periods', [9, 21, 50, 100, 200]),
        ('start_date', None),
        ('end_date', None),
        ('lookback_bars', 10),

    )
    

    def log(self, txt):
        global a_calculated_profit, a_max_trades, a_position_closed

        dt = self.datas[0].datetime.datetime(0)
        
        if txt == 'OPEN':
            print("===============OPEN===================")
            a_position_closed = False

        print(f'{dt}, {"LONG" if self.position.size > 0 else "SHORT"}, {self.data.close[0]}, {self.position.size}')
        if(txt == 'CLOSE'):
            print("Verifying Profit: ", self.position.size * (self.data.close[0] - self.position.price))
            print(f"{self.position.size} * ({self.data.close[0]} - {self.position.price})")
            a_calculated_profit += self.position.size * (self.data.close[0] - self.position.price)
            print(f"{a_calculated_profit}")
            a_position_closed = True
            print("================CLOSED==================")
            if(total_closed_positions >= a_max_trades ):
                exit()
            
    
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
        global a_position_closed
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
        was_oversold = self.bars_since_oversold is not None and self.bars_since_oversold <= self.params.lookback_bars
        was_overbought = self.bars_since_overbought is not None and self.bars_since_overbought <= self.params.lookback_bars
        crossover_bull = self.macd.macd[0] > self.macd.signal[0]
        crossover_bear = self.macd.macd[0] < self.macd.signal[0]

        self.buy_signal = was_oversold and crossover_bull
        self.sell_signal = was_overbought and crossover_bear

        
        # Long Strategy
        if self.buy_signal and self.params.enable_long_strategy:
            self.close_short()
            if a_position_closed:
                self.log("OPEN")
                self.buy(size=cerebro.broker.getcash() / self.data.close[0])
            else:
                self.set_stop_loss_take_profit('long')


        # Short Strategy
        if self.sell_signal and self.params.enable_short_strategy:
            self.close_long()
            if a_position_closed:
                self.log("OPEN")
                self.sell(size=cerebro.broker.getcash() / self.data.close[0])
            else:
                self.set_stop_loss_take_profit('short')
    

    def set_stop_loss_take_profit(self, position_type):
        global a_position_closed
        if a_position_closed:
            return
        
        if position_type == 'long':
            stop_loss = self.position.price * (1 - self.params.long_stoploss / 100)# 110 * (1 - 0.05 / 100)
            take_profit = self.position.price * (1 + self.params.long_takeprofit / 100)
        elif position_type == 'short':
            stop_loss = self.position.price * (1 + self.params.short_stoploss / 100)
            take_profit = self.position.price * (1 - self.params.short_takeprofit / 100)

        # self.sell(exectype=bt.Order.Stop, price=stop_loss)
        # self.sell(exectype=bt.Order.Limit, price=take_profit)
        if position_type == 'long' and self.data.close[0] < stop_loss:
            self.close()
            self.log("CLOSE")
        elif position_type == 'short' and self.data.close[0] > stop_loss:
            self.close()
            self.log("CLOSE")

        if position_type == 'long' and self.data.close[0] > take_profit:
            self.close()
            self.log("CLOSE")
        elif position_type == 'short' and self.data.close[0] < take_profit:
            self.close()
            self.log("CLOSE")

    def close_long(self):
        if self.position.size > 0:
            self.log("CLOSE")
            global total_closed_positions
            total_closed_positions += 1
            self.close()

    def close_short(self):
        if self.position.size < 0:
            self.log("CLOSE")
            global total_closed_positions
            total_closed_positions += 1
            self.close()

# Data preparation
cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(
    dataname='./backtrader/BTCUSDT.csv',  # Replace with your data file path
    dtformat='%m-%d-%YT%H:%M:%S.000Z',  # New format to match '2024-12-01T00:00:00.000Z'
    timeframe=bt.TimeFrame.Minutes,
    fromdate=datetime.datetime(2024, 12, 22),
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
print(f'Total Closed Positions: {total_closed_positions}')
print(f'Total Calculated Profit: {a_calculated_profit}')

# Visualization
# cerebro.plot()