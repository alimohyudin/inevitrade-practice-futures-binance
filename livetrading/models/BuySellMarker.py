import backtrader as bt

class BuySellMarker(bt.Indicator):
    lines = ('buy', 'sell',)
    plotinfo = dict(plot=True, subplot=False)
    plotlines = dict(
        buy=dict(marker='^', markersize=8.0, color='green', fillstyle='full'),
        sell=dict(marker='v', markersize=8.0, color='red', fillstyle='full'),
    )
