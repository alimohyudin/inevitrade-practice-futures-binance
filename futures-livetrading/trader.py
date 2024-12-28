import backtrader as bt
from backtrader_binance_futures import BinanceStore
from ConfigBinance.Config import Config  # Configuration file
import datetime as dt
from strategy.MACDStrategy import MACDStrategy
import asyncio
import websockets

# WebSocket server handler
async def echo_server(websocket):
    print(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # Echo the message back to the client
            await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed as e:
        print(f"Client disconnected: {e}")

async def start_server():
    server = await websockets.serve(echo_server, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == '__main__':
    # Start WebSocket server
    asyncio.run(start_server())

    
    # cerebro = bt.Cerebro(quicknotify=True)

    # coin_target = 'USDT'
    # symbol = 'BTC' + coin_target

    # store = BinanceStore(
    #     api_key=Config.BINANCE_API_KEY,
    #     api_secret=Config.BINANCE_API_SECRET,
    #     coin_target=coin_target,
    #     testnet=Config.TESTNET)

    # broker = store.getbroker()
    # cerebro.setbroker(broker)

    # from_date = dt.datetime.now(dt.UTC) - dt.timedelta(hours=48)
    # data = store.getdata(timeframe=bt.TimeFrame.Minutes, compression=3, dataname=symbol, start_date=from_date, LiveBars=True)

    # cerebro.adddata(data)

    # cerebro.addstrategy(MACDStrategy)

    # cerebro.run()
    # cerebro.plot()