import datetime as dt
import backtrader as bt
from backtrader_binance import BinanceStore
from models.BuySellMarker import BuySellMarker
from models.Position import Position
from ConfigBinance.Config import Config  # Configuration file
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


a_log_all_trades = True
a_log_trade = -1
a_total_closed_positions = 0
a_calculated_profit = 0
a_max_trades = 9999
a_position_closed = True
a_last_position = Position()
a_signal = ""
a_wait_for_order_completion = False
a_SL_or_TP_hit = False


# Trading System
class MACDStrategy(bt.Strategy):
    params = (
        ('coin_target', 'USDT'),
        ('enable_long_strategy', True),
        ('long_stoploss', 5),  # percent
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

             
    def __init__(self):
        self.markers = {data._name: BuySellMarker(data) for data in self.datas}
        self.orders = {}  # All orders as a dict, for this particularly trading strategy one ticker is one order
        for d in self.datas:  # Running through all the tickers
            self.orders[d._name] = None  # There is no order for ticker yet
        
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

        self.buy_once = {}
        self.sell_once = {}

    def next(self):
        """Arrival of a new ticker candle"""
        global a_position_closed, a_last_position, a_wait_for_order_completion, a_signal, a_SL_or_TP_hit, a_total_closed_positions, a_log_all_trades, a_log_trade
        # print("===next called===")
        for data in self.datas:  # Running through all the requested bars of all tickers
            ticker = data._name
            status = data._state  # 0 - Live data, 1 - History data, 2 - None
            _interval = self.broker._store.get_interval(data._timeframe, data._compression)
            
            # print(f'{status} | {data.datetime.datetime(0)} | {data._name} | {_interval} | {data.open[0]} | {data.high[0]} | {data.low[0]} | {data.close[0]} | {data.volume[0]} | {status}')

            if status in [0, 1]:
                if status: _state = "False - History data"
                else: _state = "True - Live data"

                # print('{} / {} [{}] - Open: {}, High: {}, Low: {}, Close: {}, Volume: {} - Live: {}'.format(
                #     bt.num2date(data.datetime[0]),
                #     data._name,
                #     _interval,  # ticker timeframe
                #     data.open[0],
                #     data.high[0],
                #     data.low[0],
                #     data.close[0],
                #     data.volume[0],
                #     _state,
                # ))

                # if status != 0: continue  # if not live - do not enter to position!

                coin_target = self.p.coin_target
                # print(f"\t - Free balance: {self.broker.getcash()} {coin_target}")

                # Very slow function! Because we are going through API to get those values...
                symbol_balance, short_symbol_name = self.broker._store.get_symbol_balance(ticker)
                # print(f"\t - {ticker} current balance = {symbol_balance} {short_symbol_name}")

                order = self.orders[data._name]  # The order of ticker
                if order and order.status == bt.Order.Submitted:  # If the order is not on the exchange (sent to the broker)
                    return  # then we are waiting for the order to be placed on the exchange, we leave, we do not continue further
                
                
                #============== My Strategy Starts Here================
                
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
                
                # print(f'{data.datetime.datetime(0)} | RSI: {self.rsi[0]} | MACD: {self.macd.macd[0]} | Signal: {self.macd.signal[0]} | Buy: {self.buy_signal} | Sell: {self.sell_signal}')
                # print(f'{was_oversold} | {was_overbought} | {crossover_bull} | {crossover_bear}')
                
                
                # Long Strategy
                if self.buy_signal and self.params.enable_long_strategy:
                    print(f"buy signal {data.datetime.datetime(0)}") 
                    self.markers[data._name].lines.buy[0] = data.close[0]

                    continue
                    
                    print("buy signal") if a_log_trade-1 == a_total_closed_positions or a_log_all_trades else None
                    a_signal = "buy"
                    a_SL_or_TP_hit = False
                    
                    self.close_short()
                    if a_position_closed and not a_wait_for_order_completion:
                        # print(f'open {cerebro.broker.getcash()} / {self.data.close[0]}')
                        self.buy(size=cerebro.broker.getcash() / self.data.close[0])
                        # self.log("OPEN")


                # Short Strategy
                if self.sell_signal and self.params.enable_short_strategy:
                    print(f"sell signal: {data.datetime.datetime(0)}")
                    self.markers[data._name].lines.sell[0] = data.close[0]

                    continue
                    print("sell signal") if a_log_trade-1 == a_total_closed_positions or a_log_all_trades else None
                    a_signal = "sell"
                    a_SL_or_TP_hit = False
                    self.close_long()
                    if a_position_closed and not a_wait_for_order_completion:                
                        # print(f'close {cerebro.broker.getcash()} / {self.data.close[0]}')
                        self.sell(size=(cerebro.broker.getcash() / self.data.close[0]))
                        # self.log("OPEN")
                # if not a_position_closed:
                #     self.set_stop_loss_take_profit()

    def notify_order(self, order):
        global a_position_closed, a_last_position, a_wait_for_order_completion

        """Changing the status of the order"""
        order_data_name = order.data._name  # Name of ticker from order
        self.log2(f'Order number {order.ref} {order.info["order_number"]} {order.getstatusname()} {"Buy" if order.isbuy() else "Sell"} {order_data_name} {order.size} @ {order.price}')
        
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
            self.log2(f"Order {order.info['name']} was not completed: {order.Status[order.status]}")
            
        if order.status == bt.Order.Completed:  # If the order is fully executed
            if order.isbuy():  # The order to buy
                print(self.orders[data._name].binance_order)  # order.executed.price, order.executed.value, order.executed.comm - you can get from here
                self.log2(f'Buy {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
            else:  # The order to sell
                print(self.orders[data._name].binance_order)  # order.executed.price, order.executed.value, order.executed.comm - you can get from here
                self.log2(f'Sell {order_data_name} @{order.executed.price:.2f}, Price {order.executed.value:.2f}, Commission {order.executed.comm:.2f}')
                self.orders[order_data_name] = None  # Reset the order to enter the position - in case of linked buy
            # self.orders[order_data_name] = None  # Reset the order to enter the position

    def notify_trade(self, trade):
        """Changing the position status"""
        if trade.isclosed:  # If the position is closed
            self.log2(f'Profit on a closed position {trade.getdataname()} Total={trade.pnl:.2f}, No commission={trade.pnlcomm:.2f}')

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
            print(f'===============================================================Long hit SL')
            a_SL_or_TP_hit = True
            # self.log("CLOSE")
        if position_type == 'short' and self.data.close[0] > stop_loss:
            self.close()
            print(f'===============================================================Short hit SL')
            a_SL_or_TP_hit = True
            # self.log("CLOSE")
        # print(f'Now {self.data.close[0]}')
        if position_type == 'long' and self.data.close[0] > take_profit:
            self.close()
            print(f'===============================================================Long hit TP')
            a_SL_or_TP_hit = True
            # self.log("CLOSE")
        if position_type == 'short' and self.data.close[0] < take_profit:
            self.close()
            print(f'===============================================================Short hit TP')
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

    def log(self, txt):
        # print("===log called=== ", txt)
        global a_total_closed_positions, a_calculated_profit, a_max_trades, a_position_closed, a_last_position

        dt = self.datas[0].datetime.datetime(0)
        
        if txt == 'OPEN':
            print(f"{a_total_closed_positions+1}===============OPEN===================")
            a_position_closed = False
            a_last_position.size = self.position.size
            a_last_position.price = self.position.price
            a_last_position.time = dt
            # print(f'{a_last_position.size}, {a_last_position.price}')

        # print(f'{dt}, {"LONG" if a_last_position.size > 0 else "SHORT"}, {self.data.close[0]}, {a_last_position.size}')
        print(f'{dt} | {"LONG" if a_last_position.size > 0 else "SHORT"} | {self.data.close[0]}')
        if(txt == 'CLOSE'):
            # print("Verifying Profit: ", a_last_position.size * (self.data.close[0] - a_last_position.price))
            # print(f"{a_last_position.size} * ({self.data.close[0]} - {a_last_position.price})")
            a_calculated_profit += a_last_position.size * (self.data.close[0] - a_last_position.price)
            # print(f"{a_calculated_profit}")
            a_position_closed = True
            a_last_position.size = 0
            a_last_position.price = 0
            print("================CLOSED==================\n")
            if(a_total_closed_positions >= a_max_trades ):
                self.print_results()
                exit()
    
    def log2(self, txt, dt=None):
        """Print string with date to the console"""
        dt = bt.num2date(self.datas[0].datetime[0]) if not dt else dt  # date or date of the current bar
        print(f'{dt.strftime("%d.%m.%Y %H:%M")}, {txt}')  # Print the date and time with the specified text to the console
    
    
    
    
    
    
    
    
    
    
    
    
    
    
if __name__ == '__main__':
    cerebro = bt.Cerebro(quicknotify=True)

    coin_target = 'USDT'  # the base ticker in which calculations will be performed
    symbol = 'BTC' + coin_target  # the ticker by which we will receive data in the format <CodeTickerBaseTicker>

    store = BinanceStore(
        api_key=Config.BINANCE_API_KEY,
        api_secret=Config.BINANCE_API_SECRET,
        coin_target=coin_target,
        testnet=False)  # Binance Storage

    # live connection to Binance - for Offline comment these two lines
    broker = store.getbroker()
    cerebro.setbroker(broker)

    # Historical 1-minute bars for the last hour + new live bars / timeframe M1
    from_date = dt.datetime.now(dt.UTC) - dt.timedelta(hours=12)
    data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=3, dataname=symbol, start_date=from_date, LiveBars=False)

    cerebro.adddata(data)  # Adding data

    cerebro.addstrategy(MACDStrategy, coin_target=coin_target)  # Adding a trading system

    cerebro.run()  # Launching a trading system
    cerebro.plot()  # Draw a chart