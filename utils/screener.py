import datetime
from backtrader import backtrader as bt
from backtrader.strategies import *
import yfinance as yf
from backtrader.feeds.pandafeed import PandasData 
from backtrader.analyzers.screener import *
import pandas as pd
from tqdm import tqdm
from datetime import date
import os


#Add data to Cerebro
# instruments = ['2303.TW', '2330.TW', '2454.TW', '3034.TW']
def screener_fn(arr_tuple): #  instruments, index
    instruments = arr_tuple[0]
    index = arr_tuple[1]
    suffix = arr_tuple[2]
    if suffix == 'AX':
        df = pd.read_csv('datas/AU300.csv')
    else:
        df = pd.read_csv('datas/TW50.csv')
    cerebro = bt.Cerebro()
    for idx in range(len(instruments)):  
        ticker = instruments[idx]
        # print(str(ticker)+'.TW')
        stock = yf.Ticker(str(ticker)+f'.{suffix}')
        try:
            data = stock.history(period='1y')
            data = data.drop(columns=['Dividends', 'Stock Splits'])
            data = PandasData(dataname=data)
            cerebro.adddata(data, name= str(ticker))
        except:
            pass
    #Add analyzer for screener
    cerebro.addanalyzer(Screener_RSI)
    cerebro.addanalyzer(Screener_SMA)
    stratList = cerebro.run(runonce=False, stdstats=False, writer=True)
    # cerebro.plot()
    # write out analyzer
    strat = stratList[0]
    stratList = []
    for x in strat.analyzers:
        x.print()
        stratList.append(x.get_analysis())
    ana_out = {'strategy':[], 'ticker':[],'name':[], 'price':[], 'value':[]}
    for dict_out in stratList:
        for s in dict_out.keys():
            if len(dict_out[s]) != 0:
                for d in dict_out[s]:
                    ana_out['strategy'].append(s)
                    ana_out['ticker'].append(d[0])
                    if suffix == 'TW':
                        ana_out['name'].append(df[df['ticker']==int(d[0])]['name'].tolist()[0])
                    else:
                        ana_out['name'].append(df[df['ticker']==d[0]]['name'].tolist()[0])
                    ana_out['price'].append(d[1])
                    ana_out['value'].append(d[2])
    # print(ana_out)
    df = pd.DataFrame.from_dict(ana_out)
    today = date.today()
    out_path = 'screen_out/{}_{}.csv'.format(today, index)
    df.to_csv(out_path,index=False,encoding = 'utf_8_sig')
    # os.system('cp -f screen_out/{}.csv ../dash/screener/{}.csv'.format(today, today))
