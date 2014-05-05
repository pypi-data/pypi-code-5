import os
import datetime
import pytz
import tzlocal
import time

import numpy as np
import pandas as pd

from pulley.brokers.ib import broker, tws
from pulley.zp.sources.splits_and_divs import CsvSplitSource, CsvDividendSource
from pulley.zp.sources import redshift, yahoo
from pulley.zp.finance.commission import PerShareWithMin

from zipline.finance.trading import SimulationParameters
from zipline.finance.slippage import FixedSlippage
from zipline.utils.tradingcalendar import get_trading_days
from zipline.protocol import BarData, SIDData, DATASOURCE_TYPE
from zipline.sources import DataPanelSource

from celery import shared_task

eastern = pytz.timezone('US/Eastern')
local_tz = tzlocal.get_localzone()

class Runner(object):
    
    def __init__(self, tickers=[], capital_base=None, mlab=None):

        assert capital_base is not None and capital_base >= 0
        assert tickers is not None and len(tickers) > 0
        
        self.algo = None
        self.sim_params = None
        self.tickers = tickers
        self.capital_base = capital_base
        self.mlab = mlab        
        self.rows_prices = None
        self.bench_price_utc = None
        
    def run(self, algo,
            tBeg=None, tEnd=None,
            commission=None,
            slippage=None,
            warn=False,
            bar_source='yahoo',
            adjusted=False):

        # Set a default algo if none is provided
        if not algo:
            raise Exception('No algo provided')
        self.algo = algo

        # set commission model
        if commission:
           self.algo.set_commission(commission)
        else:
            self.algo.set_commission(PerShareWithMin(comm_per_share=0.01, comm_min=1.0))

        # set slippage model
        if slippage:
            self.algo.set_slippage(slippage)
        else:
            self.algo.set_slippage(FixedSlippage(spread=0.0))

        # guess starting and ending dates if none are provided
        if not tEnd:
            tEnd = get_last_close()
        elif not tEnd.tzinfo:
            tEnd = local_tz.localize(tEnd)
            
        if not tBeg:
            tBeg = get_lagged_close(int(self.algo.iL), tNow=tEnd)
        elif not tBeg.tzinfo:
            tBeg = local_tz.localize(tBeg)

        self.sim_params = SimulationParameters(tBeg, tEnd, data_frequency='daily',
                                               capital_base=self.capital_base,
                                               make_new_environment=True,
                                               extra_dates=[])
        print self.sim_params

        # Don't fetch new ones if we've already got them for another run, this lets the updater method work.
        #if self.rows_prices is not None:
        #    print '----> Warning: self.rows_prices has already been initialized')
        self.rows_prices = None

        source = self.get_bar_source(tBeg, tEnd, bar_source, adjusted)

        if bar_source == 'redshift':
            bench_source, self.bench_price_utc = redshift.get_bench_source(tBeg, tEnd)
        else:
            bench_source = None

        sources = [source]

        if not warn:
            # turn off warnings
            import warnings
            warnings.filterwarnings('ignore')
        
        self.results = self.algo.run(sources, sim_params=self.sim_params, benchmark_return_source=bench_source)


    '''
    Get a list of Zipline events for each bar in our bar data source.
    '''
    def get_bar_source(self, tBeg, tEnd, bar_source, adjusted):
        
        if bar_source == 'yahoo':
            panel = yahoo.fetch(self.tickers, tBeg, tEnd, adjusted=adjusted)
            self.rows_prices = yahoo.flatten_panel(panel)
        elif bar_source == 'redshift':
            if adjusted:
                raise Exception('Redshift does not have any adjusted prices.')
            if not redshift.has_creds():
                raise Exception('No environment variables set for AWS Redshift.')
            self.rows_prices = redshift.get_data(self.tickers, tBeg, tEnd)    
        else:
            raise Exception('Unknown bar_source: %s' % bar_source)
        
        return redshift.get_price_events(self.rows_prices)   
        
    def is_up_to_date(self):
        dt_last_quote = self.rows_prices[-1][0]

        if eastern.localize(dt_last_quote) != self.algo.current_dt.astimezone(eastern):
            raise Exception('Current datetime of algorithm does not match that of the most recent quote. %s vs. %s',
                            (str(eastern.localize(dt_last_quote)), str(self.algo.current_dt.astimezone(eastern))))

        if dt_last_quote.date() != now_local().date():
            msg = 'Current date does not match that of the most recent quote. %s vs. %s' % \
                (str(dt_last_quote.date()), str(now_local().date()))
            raise Exception(msg)

        return True
    
    def ib_connect(self):
        self.ib = broker.IBBroker()
        self.ib.connect()
        self.ib.tws.reqAccountUpdates(True, '')
        self.ib.subscribe_list(self.tickers)
        if not self.ib.is_connected():
            raise Exception('Failed to connect with IB.')

    def get_positions_frame(self):
        ib_df = self.ib.get_positions_frame()
        sync_dict = {}
        
        for tkr in self.tickers:
            shares_theo = 0
            if tkr in self.algo.portfolio.positions:
                shares_theo = self.algo.portfolio.positions[tkr].amount

            shares_actual = 0
            if tkr in ib_df.ix[:, 'position']:
                shares_actual = ib_df.ix[tkr, 'position']
                
            shares_pending = 0
            if tkr in self.algo.blotter.open_orders:
                orders = self.algo.blotter.open_orders[tkr]
                for order in orders:
                    shares_pending += order.amount
                
            shares_diff1 = shares_theo - shares_actual
            shares_diff2 = (shares_theo + shares_pending) - shares_actual
            
            sync_dict[tkr] = {'shares_actual':shares_actual, 
                              'shares_theo':shares_theo,
                              'shares_pending': shares_pending,
                              'shares_diff1':shares_diff1,
                              'shares_diff2':shares_diff2,
                              }

        return pd.DataFrame.from_dict(sync_dict, orient='index')
    

    # this sync considers algo.blotter.open_orders as well
    def sync_plus(self, dry=False):
        pos_df = self.get_positions_frame()
        print pos_df
        
        if pos_df is None:
            return

        for tkr in self.tickers:
            # amt = (pos_df.shares_theo[tkr] + pos_df.shares_pending[tkr]) - pos_df.shares_actual[tkr]
            amt = pos_df.shares_diff2[tkr]
            if amt != 0:
                limit_price = self.ib.get_price(tkr)
                if dry:
                    print '%s\t%i\t%s' % (tkr, int(amt), str(limit_price))
                else:
                    if not limit_price:
                        self.ib.order(tkr, amt)
                    else:
                        self.ib.order(tkr, amt, limit_price=limit_price)


    # get a single quote
    def get_quote(self, tkr):
        return self.ib.get_quote(tkr)
    
    # gets quotes
    def get_quotes(self):
        quote_dict = {}
        prices_ok = True
        for tkr in self.tickers:
            price, size = self.get_quote(tkr)
            if not price:
                prices_ok = False
            quote_dict[tkr] = {'price': price, 'size': size}
        return quote_dict, prices_ok


    # update the rows of database-IB quote hybrid prices
    def update(self, dry=False):        
        dt = datetime.datetime.now()
        quotes, prices_ok = self.get_quotes()
        if not prices_ok:
            raise Exception('Bad prices in bar data.')
        for tkr, quote in quotes.iteritems():
            # Fake a big enough quote size to not trigger VolumeShareSlippage
            self.rows_prices.append((dt, tkr, quote['price'], 1000000)) #quote['size']))

    # get reading for market open
    def pre_open(self, algo=None, dry=False, check_dates=True, bar_source='yahoo'):

        # run with a minimum window of history
        self.run(algo, commission=None, slippage=None, bar_source=bar_source)

        # check that algo is aware of newest data
        if check_dates:
            self.is_up_to_date()

        # connect to IB
        self.ib_connect()

        # sleep while IB initializes
        print '----> Sleeping for 5 seconds...'
        time.sleep(5)

        # send any new orders
        print '----> Synchronizing...'
        self.sync_plus(dry=dry)

        # close everything down
        self.ib.disconnect()

        

@shared_task
def start_rws():
    tws.run()
    
@shared_task
def on_pre_open(dry=False, check_dates=True):
    return '----> Event fired for pre open, local time is: %s' % now_local()

@shared_task
def on_market_open():
    return '----> Event fired for market open, local time is: %s' % now_local()

# helpers
def now_local():
    return datetime.datetime.now() #local_tz.localize(datetime.datetime.now())

def get_last_close():
    return eastern.localize(datetime.datetime.now() \
                                + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

def get_lagged_close(iLag, tNow=None):
    if tNow == None:
        tNow = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    trading_days = get_trading_days(tNow - datetime.timedelta(days=int(iLag*1.5)), tNow)
    return trading_days[-iLag-1]
