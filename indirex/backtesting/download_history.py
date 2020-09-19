""" Downloads historical data from Quandl and formats it 
Usage: python3 download_history.py <history, shares_outstanding> <ticker_file>"""

import time
import pickle
import requests
from pathlib import Path
import sys
import quandl
from indirex.hidden import *

def download_history():
    """ Uses the first argument as a file containing a list of stocks to download history for """
    for t in open(f'../data/{sys.argv[2]}').readlines():
        ticker = t.strip()
        try:
            data = quandl.get(f'EOD/{ticker}', authtoken=QUANDL_API_KEY)
            data = data.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Dividend', 'Split'])
            data = data.rename(columns={'Adj_Open': 'Open', 'Adj_High': 'High', 'Adj_Low': 'Low', 'Adj_Close': 'Close', 'Adj_Volume': 'Volume'})
            pickle.dump(data, open(f'../data/eod_history/{ticker}.pkl', 'wb+'))
            print(ticker)
        except:
            print(f'Error on ticker {ticker}')
            pass # If an error occurs, just move on

def record_shares_outstanding():
    """ Uses the list of tickers and records the outstanding shares for each company """
    outstanding = pickle.load(open(f'../data/shares_outstanding.pkl', 'rb'))
    for t in open(f'../data/{sys.argv[2]}').readlines():
        ticker = t.strip()
        try:
            r = requests.get(f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}')
            outstanding[ticker] = int(r.json()['SharesOutstanding'])
            print(ticker, outstanding[ticker])
        except:
            print(f'Could not retrieve outstanding shares on {ticker}')
            pass # If an error occurs, just move on
        time.sleep(12.2) # API allows 5 calls per minute / 500 calls per day
    pickle.dump(outstanding, open(f'../data/shares_outstanding.pkl', 'wb+'))


if __name__ == "__main__":
    if sys.argv[1] == 'history':
        download_history()
    if sys.argv[1] == 'shares_outstanding':
        record_shares_outstanding()