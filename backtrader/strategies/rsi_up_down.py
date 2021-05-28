#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import backtrader as bt
import backtrader.indicators as btind
from backtrader.strategies.sma_crossover import MAcrossover
import pandas as pd
from datetime import date
import pathlib

class RSI_up_down(bt.Strategy):
    '''This is a long-only strategy which operates on a moving average cross

    Note:
      - Although the default

    Buy Logic:
      - No position is open on the data

      - The rsi up > 50 and day volume > 1.5 * avg(volume, 5 days)

      - The rsi down < 25 and day volume > 1.5 * avg(volume, 5 days)

    Sell Logic:
      - A position exists on the data

      - down below five day lowest price

    Order Execution Type:
      - Market

    '''
    alias = ('RSI_up',)

    params = (('period',20), ('devfactor',2), ('sma',5), ('min_volume', 5000), ('times_volume', 1.2), \
              ('up_rsi', 50), ('dojo_ratio', 0.1), ('d0', None), ('type', 'up'))

    def __init__(self):
        self.order = None
        self.smavolume= bt.indicators.MovingAverageSimple(self.datas[0].volume, period = self.params.sma)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.datas[0]) 
        self.df_out = pd.DataFrame()
        self.prev_price = []
        self.buy_price = None
        self.ticker = self.params.d0
        self.init_fund = self.broker.getvalue()
        # self.ticker
        self.fname = f'strategy_out/{date.today()}'
        pathlib.Path(self.fname).mkdir(parents=True, exist_ok=True)
        with open(f'{self.fname}/rsi_{self.params.type}_{self.ticker}.txt', 'w') as f:
            f.write('')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization
        with open(f'{self.fname}/rsi_{self.params.type}_{self.ticker}.txt', '+a') as f:
            f.write(f'{dt.isoformat()}\t{txt}\n')

    def next(self):
         # Check for open orders
        if self.order:
          return
        data = self.datas[0]
        rsi = self.rsi
        smavolume = self.smavolume
        sell_day = 2
        if (len(self.prev_price)>sell_day):
            self.prev_price.pop(0)
        self.prev_price.append(data.low[0])
        # print(rsi.lines.rsi[0], (data.close[0] - data.low[0])/data.low[0])
        # print(data.close[0], data.datetime.date(0), data.close[1], data.datetime.date(1))
        # print(data.close[0], data.low[0], data.volume[0], self.rsi.lines.rsi[0], self.smavolume.lines.sma[0])
        # Check if we are in the market
        if not self.position:
            dojo = (data.close[0] - data.low[0])/data.low[0]
            if self.params.type == 'up':
                if rsi.lines.rsi[0] >= self.params.up_rsi and dojo > self.params.dojo_ratio \
                        and data.volume[0] >  self.params.min_volume \
                        and smavolume.lines.sma[0] * self.params.times_volume < data.volume[0]:
                    self.log(f'RSI up BUY CREATE\t{data.close[0]:2f}')
                    self.buy_price = data.close[0]
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
            elif self.params.type == 'down':
                if rsi.lines.rsi[0] <= 25 and data.volume[0] > self.params.min_volume \
                    and dojo > self.params.dojo_ratio :
                    self.log(f'RSI down BUY CREATE\t{data.close[0]:2f}')
                    self.buy_price = data.close[0]
                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()
            else:
                if (rsi.lines.rsi[0] >= self.params.up_rsi and dojo > self.params.dojo_ratio \
                        and data.volume[0] >  self.params.min_volume \
                        and smavolume.lines.sma[0] * self.params.times_volume < data.volume[0]) \
                    or (rsi.lines.rsi[0] <= 25 and data.volume[0] > self.params.min_volume \
                        and dojo > self.params.dojo_ratio):
                        self.log(f'RSI all BUY CREATE\t{data.close[0]:2f}')
                        self.buy_price = data.close[0]
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()
                
        # elif data.close[0] < min(self.prev_price[:sell_day]):
        #   # We are already in the market, look for a signal to CLOSE trades
        #     self.log(f'CLOSE CREATE\t{data.close[0]:2f}\t{100*(data.close[0]-self.buy_price)/self.buy_price:2f}%')
        #     self.buy_price = None
        #     self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
          # An active Buy/Sell order has been submitted/accepted - Nothing to do
          return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
          if order.isbuy():
            self.log(f'BUY EXECUTED,\t{order.executed.price:.2f}')
          elif order.issell():
            self.log(f'SELL EXECUTED,\t{order.executed.price:.2f}')
          self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
          self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None
    
    def stop(self):
        if self.position:
            data = self.datas[0]
            self.log(f'CLOSE At Last Day\t{data.close[0]:2f}\t{100*(data.close[0]-self.buy_price)/self.buy_price:2f}%')
            self.buy_price = None
            self.order = self.close()
        self.log(f'start\t{self.init_fund}\tend\t{self.broker.getvalue()}\t{((self.broker.getvalue()-self.init_fund)/self.init_fund)*100:.2f}%')
        # print("value ", self.broker.getvalue())
