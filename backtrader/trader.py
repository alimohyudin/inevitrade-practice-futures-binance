import backtrader as bt
import datetime
from models.Position import Position


a_log_trade = -1
a_total_closed_positions = 0
a_calculated_profit = 0
a_max_trades = 9999
a_position_closed = True
a_last_position = Position()
a_signal = ""
a_wait_for_order_completion = False
a_SL_or_TP_hit = False

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
        # print("===log called=== ", txt)
        global a_total_closed_positions, a_calculated_profit, a_max_trades, a_position_closed, a_last_position

        dt = self.datas[0].datetime.datetime(0)
        
        if txt == 'OPEN':
            # print(f"{a_total_closed_positions+1}===============OPEN===================")
            a_position_closed = False
            a_last_position.size = self.position.size
            a_last_position.price = self.position.price
            a_last_position.time = dt
            # print(f'{a_last_position.size}, {a_last_position.price}')

        # print(f'{dt}, {"LONG" if a_last_position.size > 0 else "SHORT"}, {self.data.close[0]}, {a_last_position.size}')
        # print(f'{dt} | {"LONG" if a_last_position.size > 0 else "SHORT"} | {self.data.close[0]}')
        if(txt == 'CLOSE'):
            # print("Verifying Profit: ", a_last_position.size * (self.data.close[0] - a_last_position.price))
            # print(f"{a_last_position.size} * ({self.data.close[0]} - {a_last_position.price})")
            a_calculated_profit += a_last_position.size * (self.data.close[0] - a_last_position.price)
            # print(f"{a_calculated_profit}")
            a_position_closed = True
            a_last_position.size = 0
            a_last_position.price = 0
            # print("================CLOSED==================\n")
            if(a_total_closed_positions >= a_max_trades ):
                self.print_results()
                exit()
            
    def notify_order(self, order):
        global a_position_closed, a_last_position, a_wait_for_order_completion
        # print(f'========Notify_order')
        # print(f'========Status {order}')
        # print(f'========Status {order.Status} {[order.Rejected]}')
        if order.status in [order.Completed]:
            a_wait_for_order_completion = False
            if order.isbuy():
                if a_position_closed:
                    self.log("OPEN")
                else:
                    self.log("CLOSE")
                    
                    if not a_SL_or_TP_hit:
                        a_wait_for_order_completion = True
                        if a_signal == "buy":
                            # print(f'open {cerebro.broker.getcash()} / {self.data.close[0]}')
                            self.buy(size = (cerebro.broker.getvalue() - 1) / self.data.close[0])
                        elif a_signal == "sell":
                            self.sell(size = (cerebro.broker.getvalue() - 1)/ self.data.close[0])
            elif order.issell():
                if a_position_closed:
                    self.log("OPEN")
                else:
                    self.log("CLOSE")
                    
                    if not a_SL_or_TP_hit:
                        a_wait_for_order_completion = True
                        if a_signal == "buy":
                            self.buy(size = (cerebro.broker.getvalue() - 1) / self.data.close[0])
                        elif a_signal == "sell":
                            self.sell(size = (cerebro.broker.getvalue() - 1) / self.data.close[0])
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"Order {order.info['name']} was not completed: {order.Status[order.status]}")
            
    # def notify_trade(self, trade):
    #     print(f'')
        
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
        global a_position_closed, a_last_position, a_wait_for_order_completion, a_signal, a_SL_or_TP_hit, a_total_closed_positions, a_log_trade
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
            print("buy signal") if a_log_trade-1 == a_total_closed_positions else None
            a_signal = "buy"
            a_SL_or_TP_hit = False
            
            self.close_short()
            if a_position_closed and not a_wait_for_order_completion:
                # print(f'open {cerebro.broker.getcash()} / {self.data.close[0]}')
                self.buy(size=cerebro.broker.getcash() / self.data.close[0])
                # self.log("OPEN")


        # Short Strategy
        if self.sell_signal and self.params.enable_short_strategy:
            print("sell signal") if a_log_trade-1 == a_total_closed_positions else None
            a_signal = "sell"
            a_SL_or_TP_hit = False
            self.close_long()
            if a_position_closed and not a_wait_for_order_completion:                
                # print(f'close {cerebro.broker.getcash()} / {self.data.close[0]}')
                self.sell(size=(cerebro.broker.getcash() / self.data.close[0]))
                # self.log("OPEN")
        if not a_position_closed:
            self.set_stop_loss_take_profit()

    def set_stop_loss_take_profit(self):
        global a_position_closed, a_last_position, a_SL_or_TP_hit
        stop_loss = None
        take_profit = None
        
        position_type = 'long' if a_last_position.size > 0 else 'short'
        
        if position_type == 'long':
            stop_loss = a_last_position.price * (1 - self.params.long_stoploss / 100)# 110 * (1 - 0.05 / 100)
            take_profit = a_last_position.price * (1 + self.params.long_takeprofit / 100)
        elif position_type == 'short':
            stop_loss = a_last_position.price * (1 + self.params.short_stoploss / 100)
            take_profit = a_last_position.price * (1 - self.params.short_takeprofit / 100)

        # print(f'SL {stop_loss}, TP {take_profit}')

        # self.sell(exectype=bt.Order.Stop, price=stop_loss)
        # self.sell(exectype=bt.Order.Limit, price=take_profit)
        if position_type == 'long' and self.data.close[0] < stop_loss:
            self.close()
            # print(f'===============================================================Long hit SL')
            a_SL_or_TP_hit = True
            # self.log("CLOSE")
        if position_type == 'short' and self.data.close[0] > stop_loss:
            self.close()
            # print(f'===============================================================Short hit SL')
            a_SL_or_TP_hit = True
            # self.log("CLOSE")
        # print(f'Now {self.data.close[0]}')
        if position_type == 'long' and self.data.close[0] > take_profit:
            self.close()
            # print(f'===============================================================Long hit TP')
            a_SL_or_TP_hit = True
            # self.log("CLOSE")
        if position_type == 'short' and self.data.close[0] < take_profit:
            self.close()
            # print(f'===============================================================Short hit TP')
            a_SL_or_TP_hit = True
            # self.log("CLOSE")

    def close_long(self):
        if self.position.size > 0:
            global a_total_closed_positions
            a_total_closed_positions += 1
            self.close()
            # self.log("CLOSE")

    def close_short(self):
        if self.position.size < 0:
            global a_total_closed_positions
            a_total_closed_positions += 1
            self.close()
            # self.log("CLOSE")

    def print_results(self):
        global a_total_closed_positions, a_calculated_profit
        print(f"Total Closed Positions: {a_total_closed_positions}")
        print(f"Total Calculated Profit: {a_calculated_profit}")
        print(f"Final Portfolio Value: {cerebro.broker.getvalue()}")








# Data preparation
cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(
    dataname='./backtrader/BTCUSDT-3min-3mon.csv',  # Replace with your data file path
    dtformat='%m-%d-%YT%H:%M:%S.000Z',  # New format to match '2024-12-01T00:00:00.000Z'
    timeframe=bt.TimeFrame.Minutes,
    fromdate=datetime.datetime(2024, 10, 1),
    todate=datetime.datetime(2024, 12, 31),
    compression=1,
    openinterest=-1,
)
print(len(data))
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(MACDStrategy)

# Run
cerebro.broker.setcash(1000)
cerebro.broker.setcommission(commission=0.0)
print(f'Starting Portfolio Value: {cerebro.broker.getvalue()}')
cerebro.run()
print(f'Ending Portfolio Value: {cerebro.broker.getvalue()}')
print(f'Total Closed Positions: {a_total_closed_positions}')
print(f'Total Calculated Profit: {a_calculated_profit}')

# Visualization
# cerebro.plot()