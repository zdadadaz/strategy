from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
from backtrader.utils.dateintern import num2time

class Screener_RSI(bt.Analyzer):
    params = (('period',20), ('devfactor',2), ('sma',5))

    def start(self):
        # self.bband = {data: bt.indicators.BollingerBands(data,
        #         period=self.params.period, devfactor=self.params.devfactor)
        #         for data in self.datas}
        self.smavolume= {data: bt.indicators.MovingAverageSimple(data.volume, period = self.params.sma) for data in self.datas}
        self.rsi = {data:bt.indicators.RelativeStrengthIndex(data) for data in self.datas}
        self.rets['rsi_down_25'] = list()
        self.rets['rsi_up_50_doji'] = list()

    def get_analysis(self):
        return self.rets

    def stop(self):
        # for data, band in self.bband.items():
        #     node = data._name, data.close[0], round(band.lines.bot[0], 2)
        #     if data > band.lines.bot:
        #         self.rets['over'].append(node)
        #     else:
        #         self.rets['under'].append(node)

        # data.datetime.datetime()
        for data, rsi in self.rsi.items():
            node = data._name, round(data.close[0],2), round(rsi.lines.rsi[0], 2)
            # print('avg vol, cur vol',self.smavolume[data].lines.sma[0], self.data.volume[0])
            dojo = (data.close[0] - data.low[0])/data.low[0]
            if rsi.lines.rsi[0] >=50 and dojo > 0.01 \
                and self.data.volume[0]>5000 and self.smavolume[data].lines.sma[0]*1.5 < self.data.volume[0]:
                self.rets['rsi_up_50_doji'].append(node)
            if rsi.lines.rsi[0] <= 25 and self.data.volume[0]>5000 and dojo > 0.01:
                self.rets['rsi_down_25'].append(node)

class Screener_SMA(bt.Analyzer):
    params = (('sma_fast',30), ('sma_slow',10))

    def start(self):
        # self.bband = {data: bt.indicators.BollingerBands(data,
        #         period=self.params.period, devfactor=self.params.devfactor)
        #         for data in self.datas}
        self.smaslow= {data: bt.indicators.MovingAverageSimple(data, period = self.params.sma_slow) for data in self.datas}
        self.smafast= {data: bt.indicators.MovingAverageSimple(data, period = self.params.sma_fast) for data in self.datas}
        self.rets['sma_up'] = list()
        self.rets['sma_down'] = list()
        self.crossover = {data:bt.ind.CrossOver(self.smaslow[data], self.smafast[data]) for data in self.smaslow.keys() }
    def get_analysis(self):
        return self.rets

    def stop(self):
        for data, crossover in self.crossover.items():
            node = data._name, round(data.close[0],2), round(crossover.lines.crossover[0], 2)
            if crossover.lines.crossover[0]>0:
                self.rets['sma_up'].append(node)
            elif crossover.lines.crossover[0]<0:
                self.rets['sma_down'].append(node)
