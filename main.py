import yfinance as yf
from backtrader.feeds.pandafeed import PandasData 
from backtrader import backtrader as bt
from backtrader.strategies import *
from backtrader.sizers import *
import pandas as pd
from tqdm import tqdm


# declare
cerebro = bt.Cerebro()
# cerebro.addstrategy(RSI_up_down, type='up')
cerebro.addstrategy(MA_CrossOver)
# cerebro.addstrategy(Fibpivot)
cerebro.addsizer(FixedSize)

# input data
suffix = 'AX' #'AX' or 'TW'
if suffix == 'TW':
    df = pd.read_csv('datas/TW50.csv')
else:
    df = pd.read_csv('datas/AU300.csv')
instruments = list(df['ticker'])
for idx in tqdm(range(1)): # len(instruments) 
    # ticker = instruments[idx]
    # ticker = 2615
    ticker = 'SKC'
    stock = yf.Ticker(str(ticker)+f'.{suffix}')
    data = stock.history(period='1y')
    print(len(data))
    try:
        data = data.drop(columns=['Dividends', 'Stock Splits'])
        data = PandasData(dataname=data)
        cerebro.adddata(data, name= str(ticker))
        # cerebro.resampledata(data, timeframe=bt.TimeFrame.Months)
    except:
        pass

# data = stock.history(period='1y')
# data = data.drop(columns=['Dividends', 'Stock Splits'])
# data = PandasData(dataname=data)
# cerebro.adddata(data)
start = cerebro.broker.getvalue()
cerebro.run()
end = cerebro.broker.getvalue()
print('start: {}, end: {}, profit: {}'.format(start, end, end-start))
cerebro.plot()
