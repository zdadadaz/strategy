import yfinance as yf
from backtrader.feeds.pandafeed import PandasData 
from backtrader import backtrader as bt
from backtrader.strategies import *
from backtrader.sizers import *
import pandas as pd
from tqdm import tqdm

def strategy_fn(tuple_in):
    ticker = tuple_in[0]
    type = tuple_in[1]
    # declare
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(300.0) # your asset /1000
    cerebro.addstrategy(RSI_up_down, d0=ticker, type=type)
    cerebro.addsizer(FixedSize)
    # input data 
    stock = yf.Ticker(str(ticker)+'.TW')  # need change suffix
    data = stock.history(period='1y')
    try:
        data = data.drop(columns=['Dividends', 'Stock Splits'])
        if len(data) >10:
            data = PandasData(dataname=data)
            cerebro.adddata(data, name= str(ticker))
            # cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)
    except:
        pass
    start = cerebro.broker.getvalue()
    cerebro.run()
    end = cerebro.broker.getvalue()
    # print('start: {}, end: {}, profit: {}'.format(start, end, end-start))
    # cerebro.plot()

