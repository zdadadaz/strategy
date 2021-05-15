from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt


class LongOnly(bt.Sizer):
    params = (('stake', 1),)
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            print('buy',self.p.stake,comminfo)
            return self.p.stake

        # Sell situation
        position = self.broker.getposition(data)
        print('pos',position.size)
        if position.size<=0:
            return 0  # do not sell if nothing is open

        print('sell',self.p.stake)
        return self.p.stake