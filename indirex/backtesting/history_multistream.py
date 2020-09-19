import pandas as pd
import pickle

class HistoryMultiStream:
    """ Keeps multiple streams of ticker history in sync with one another and forward fills any missing data"""

    def __init__(self, tickers):
        self.tickers = tickers
        self.frames = {t:pickle.load(open(f'../data/eod_history/{t}.pkl', 'rb')) for t in tickers}
        self.start_date = self.get_youngest()
        self.end_date = self.get_most_recent()
        self.days_data = {}

    def get_youngest(self):
        """ Gets the youngest stock in the portfolio
        determines when backtesting should start, before would be invalid """
        largest_date = self.frames[self.tickers[0]].iloc[0].name
        for ticker, data in self.frames.items():
            largest_date = max(largest_date, data.iloc[0].name)
        return largest_date

    def get_most_recent(self):
        """ Gets the most date on the most recent piece of data """
        most_recent = self.frames[self.tickers[0]].iloc[-1].name
        for ticker, data in self.frames.items():
            most_recent = max(most_recent, data.iloc[-1].name)
        return most_recent

    def get_todays_data(self):
        """ Get's the actual days data
        Assumes data has been updated from Quandl today """
        todays_data = {}
        for ticker, data in self.frames.items():
            try:
                todays_data[ticker] = data.iloc[-1]
            except KeyError:
                pass # There's no data for this date
        return todays_data

    def populate_days_data(self, date):
        """ Generates a dictionary of ticker:dataframes for a given date
        returns boolean saying whether there is any new data"""
        new_data = False
        for ticker, data in self.frames.items():
            try:
                self.days_data[ticker] = data.loc[date]
                new_data = True
            except KeyError:
                pass # There's no data for this date
        return new_data

    def stream_data(self):
        """ Generates data since the moment all of the stocks hit the market """
        for index in range((self.end_date - self.start_date).days):
            if self.populate_days_data(self.start_date + pd.Timedelta(days=index)):
                yield self.days_data