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


class MA_CrossOver(bt.Strategy):
    '''This is a long-only strategy which operates on a moving average cross

    Note:
      - Although the default

    Buy Logic:
      - No position is open on the data

      - The ``fast`` moving averagecrosses over the ``slow`` strategy to the
        upside.

    Sell Logic:
      - A position exists on the data

      - The ``fast`` moving average crosses over the ``slow`` strategy to the
        downside

    Order Execution Type:
      - Market

    '''
    alias = ('SMA_CrossOver',)

    params = (
        # period for the fast Moving Average
        ('fast', 10),
        # period for the slow moving average
        ('slow', 30),
        # moving average to use
        ('_movav', btind.MovAv.SMA)
    )

    def __init__(self):
        sma_fast = self.p._movav(period=self.p.fast)
        sma_slow = self.p._movav(period=self.p.slow)

        self.buysig = btind.CrossOver(sma_fast, sma_slow)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization

    def next(self):
        if self.position.size:
            if self.buysig < 0:
                self.sell()

        elif self.buysig > 0:
            self.buy()

class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        self.crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, self.crossover)
        
    def next(self):
        if self.crossover > 0:
            # should be in size 
            # self.order_target_percent(target=0.5)
            self.buy()
        elif self.crossover < 0:
            self.sell()

class MAcrossover(bt.Strategy): 
    # Moving average parameters
    params = (('pfast',10),('pslow',30),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization

    def __init__(self):
        self.dataclose = self.datas[0].close
        
		# Order variable will contain ongoing order details/status
        self.order = None

        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
                        period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
                        period=self.params.pfast)
        self.crossover = bt.ind.CrossOver(self.slow_sma, self.fast_sma)
        self.fib = btind.FibonacciPivotPoint(self.data1)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
          # An active Buy/Sell order has been submitted/accepted - Nothing to do
          return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
          if order.isbuy():
            self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
          elif order.issell():
            self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
          self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
          self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):
        # Check for open orders
        if self.order:
          return

        # Check if we are in the market
        if not self.position:
          # We are not in the market, look for a signal to OPEN trades
          #If the 20 SMA is above the 50 SMA
          if self.crossover > 0:
            self.log(f'BUY CREATE {self.dataclose[0]:2f}')
            # Keep track of the created order to avoid a 2nd order
            self.order = self.buy()
          # #Otherwise if the 20 SMA is below the 50 SMA   
          # elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
          #   self.log(f'SELL CREATE {self.dataclose[0]:2f}')
          #   # Keep track of the created order to avoid a 2nd order
          #   self.order = self.sell()
        elif self.crossover < 0:
          # We are already in the market, look for a signal to CLOSE trades
            self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
            self.order = self.close()

class Fibpivot(bt.Strategy): 
    # Moving average parameters
    params = (('pfast',10),('pslow',30),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') # Comment this line when running optimization

    def __init__(self):
        self.dataclose = self.datas[0].close
        
		# Order variable will contain ongoing order details/status
        self.order = None

        # Instantiate moving averages
        self.fib = btind.FibonacciPivotPoint(self.data1)
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
          # An active Buy/Sell order has been submitted/accepted - Nothing to do
          return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
          if order.isbuy():
            self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
          elif order.issell():
            self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
          self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
          self.log('Order Canceled/Margin/Rejected')

        # Reset orders
        self.order = None

    def next(self):
        # Check for open orders
        if self.order:
          return

        # Check if we are in the market
        if not self.position:
          # We are not in the market, look for a signal to OPEN trades
            
          #If the 20 SMA is above the 50 SMA
          if self.fib.lines.s1 > self.dataclose[0]:
            self.log(f'BUY CREATE {self.dataclose[0]:2f}')
            # Keep track of the created order to avoid a 2nd order
            self.order = self.buy()
          # #Otherwise if the 20 SMA is below the 50 SMA   
          # elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
          #   self.log(f'SELL CREATE {self.dataclose[0]:2f}')
          #   # Keep track of the created order to avoid a 2nd order
          #   self.order = self.sell()
        elif self.fib.lines.r2 < self.dataclose[0]:
          # We are already in the market, look for a signal to CLOSE trades
            self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
            self.order = self.close()