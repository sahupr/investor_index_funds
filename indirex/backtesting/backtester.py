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
    
    def get_chart(self):
        """ Runs the backtest and reports metrics """
        index_price = []
        capital = 100
        shares = {}
        for day, stream_frame in enumerate(self.data_stream.stream_data()):
            # Rebalance if it's time based on opening prices
            if day % self.rebalance_period == 0:
                market_caps = self.get_market_caps(stream_frame)
                total_cap = sum(market_caps.values())
                for ticker in self.tickers:
                    cap_weight = market_caps[ticker] / total_cap
                    shares[ticker] = (capital * cap_weight) / stream_frame[ticker]['Open']
            # Update the capital we have based on new daily share prices at closing
            capital = 0
            for ticker, dataframe in stream_frame.items():
                capital += dataframe['Close'] * shares[ticker]
            date = stream_frame[self.tickers[0]].name.value/1000000000
            index_price.append((date, capital))
        print(self.get_wise_investment_amount())
        return index_price

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
        for ticker, dataframe in dict_frame.items():
            caps[ticker] = dataframe['Close'] * self.outstanding[ticker]
        return caps