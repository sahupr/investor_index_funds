import pandas as pd
import numpy as np
import time
from indirex.backtesting.history_multistream import HistoryMultiStream
import matplotlib.pyplot as plt
import pickle

class CapWeightedBacktester:
    """ Reports date-aligned, historical performance metrics for a cap-weighted index
    fund based on a list of tickers """

    def __init__(self, tickers, rebalance_period):
        self.tickers = tickers
        self.data_stream = HistoryMultiStream(self.tickers)
        outstanding_shares = pickle.load(open(f'../data/shares_outstanding.pkl', 'rb'))
        self.outstanding = {ticker:outstanding_shares[ticker] for ticker in self.tickers}
        self.rebalance_period = rebalance_period
        self.spy_pair = []
        self.rebalance_points = []
        self.chart = None
    
    def get_chart(self):
        """ Runs the backtest and reports metrics """
        if self.chart is None:
            index_price = []
            capital = 100
            shares = {}
            for day, stream_frame in enumerate(self.data_stream.stream_data()):
                # Update the spy pair
                date = stream_frame[self.tickers[0]].name.value/1000000000
                self.spy_pair.append((date, stream_frame['SPY']['Close']))
                # Rebalance if it's time based on opening prices
                rebalanced = False
                if day % self.rebalance_period == 0:
                    rebalanced = True
                    market_caps = self.get_market_caps(stream_frame)
                    total_cap = sum(market_caps.values())
                    for ticker in self.tickers:
                        cap_weight = market_caps[ticker] / total_cap
                        shares[ticker] = (capital * cap_weight) / stream_frame[ticker]['Open']
                # Update the capital we have based on new daily share prices at closing
                capital = 0
                for ticker in self.tickers:
                    capital += stream_frame[ticker]['Close'] * shares[ticker]
                index_price.append((date, capital))
                if rebalanced:
                    self.rebalance_points.append((date, capital))
            self.finished = True
            self.chart = index_price
        return self.chart

    def get_rebalance_chart(self):
        """ Returns the points on the graph where a rebalance had just occured """
        if self.chart is not None:
            return self.rebalance_points
        else:
            raise('Unable to access rebalance before creation of base chart')

    def get_spy_chart(self):
        """ Returns the chart for the Spyder S&P 500 index fund over the same period
        to compare performance of the two
        ** must finish backtest first ** """
        if self.chart is not None:
            return self.spy_pair
        else:
            raise('Unable to access SPY chart before creation of base chart')

    def get_post_analysis(self):
        """ Returns a list containing key metrics on the user index:
            - Average yearly percentage returns compared to S&P500
            - Whether it outperformed the S&P 500 over the same period
            - A diversification score based on the number of stocks included """
        if self.chart is not None:
            # Calculate average yearly returns of index
            total_return = self.chart[-1][1] - self.chart[0][1]
            timeframe = self.chart[-1][0] - self.chart[0][0]
            total_multiplier = total_return / 100.0
            years = timeframe / (365.0 * 24 * 60 * 60)
            average_index_return = total_multiplier ** (1.0 / years)
            # Calculate average yearly returns of SPY
            total_return = self.spy_pair[-1][1] - self.spy_pair[0][1]
            total_spy_multiplier = total_return / self.spy_pair[0][1]
            average_spy_return = total_spy_multiplier ** (1.0 / years)
            # Determine whether it outperformed
            outperformed = total_multiplier > total_spy_multiplier
            # Give it a diversification score
            diversification_score = len(self.tickers) / 100
            return {'Average yearly returns for your ticker set': average_index_return,
                    'Average yearly returns for the S&P 500': average_spy_return,
                    'Outperformed the market': outperformed,
                    'Diversity Ranking': diversification_score,
                    'Investment needed to maintain proper weighting': self.get_wise_investment_amount()}
        else:
            raise('Unable to access analysis before creation of base chart')

    def get_wise_investment_amount(self):
        """ Given the share prices and market caps of the company, gives an investment
        amount that would make the created of the fund feasible, all weights are within 3%
        of what they should be i.e. $100 couldn't buy a share of most companies let alone
        a cap weighted portfolio of a whole list"""
        todays_data = self.data_stream.get_todays_data()
        market_caps = self.get_market_caps(todays_data)
        total_cap = sum(market_caps.values())
        share_prices = {ticker:todays_data[ticker]['Close'] for ticker in self.tickers}
        cap_weights = {ticker:(market_caps[ticker] / total_cap) for ticker in self.tickers}
        mins = [share_prices[ticker]/(cap_weights[ticker] - .03) for ticker in self.tickers]
        return max(mins)

    def get_market_caps(self, dict_frame):
        """ Returns a dictionary of the market caps for the tickers for a Multistream data dict """
        caps = {}
        for ticker in self.tickers:
            caps[ticker] = dict_frame[ticker]['Close'] * self.outstanding[ticker]
        return caps