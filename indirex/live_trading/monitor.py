import alpaca_trade_api as tradeapi
from indirex.hidden import APCA_ID, APCA_KEY, APCA_URL
import time
import pickle

class AccountManager:
    """ Monitors the Alpaca.markets account """

    def __init__(self):
        self.api = tradeapi.REST(APCA_ID, APCA_KEY, APCA_URL, 'v2')

    def get_portfolio_balance(self):
        """ Requests the portfolio balance from the API """
        account = self.api.get_account()
        time.sleep(60/200)
        return float(account.equity)

    def rebalance_portfolio(self, tickers):
        """ Attempts to rebalance the users portfolio according to the cap weights 
        will cut off any fractional shares rather than optimize """
        try:
            self.api.cancel_all_orders()
            time.sleep(60/200)
            # Load in the outstanding shares data
            outstanding = pickle.load(open('../data/shares_outstanding.pkl', 'rb'))
            outstanding = {t:outstanding[t] for t in tickers}
            # Get the total account equity from Alpaca
            total_equity = self.get_portfolio_balance()
            # Get the prices of each stock we want to own
            last_prices = {}
            for ticker in tickers:
                last_prices[ticker] = self.api.get_last_trade(ticker).price
                time.sleep(60/200)
            # Calculate the market caps and weights
            market_caps = {t:last_prices[t] * outstanding[t] for t in tickers}
            total_cap = sum(market_caps.values())
            cap_weights = {t:market_caps[t]/total_cap for t in tickers}
            # Calculate how many shares we want for each stock
            target_shares = {t:int((cap_weights[t] * total_equity) / last_prices[t]) for t in tickers}
            # Calculate how many shares we currently own for each stock
            current_shares = {t:0 for t in tickers}
            for position in self.api.list_positions():
                current_shares[position.symbol] = int(position.qty)
            time.sleep(60/200)
            # Buy or sell the difference for each
            deltas = {t:(target_shares[t] - current_shares[t]) for t in tickers}
            for ticker, delta in deltas.items():
                if delta > 0:
                    self.api.submit_order(
                        ticker,
                        abs(delta),
                        'buy',
                        'market',
                        'gtc',
                    )
                    time.sleep(60/200)
                if delta < 0:
                    self.api.submit_order(
                        ticker,
                        abs(delta),
                        'sell',
                        'market',
                        'gtc',
                    )
                    time.sleep(60/200)
        except Exception as e:
            raise e