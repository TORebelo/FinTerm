import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import utils as ut
import constants as ct
import logging as log


class Portfolio:
    def __init__(self, api_key, initial_stocks=None):
        self.api_key = api_key
        self.stocks = {}
        self.price_cache = {}
        self.retry_delay = 1  # Reduced delay between API calls
        self.max_workers = 3    # Number of parallel threads

        # Pre-fetch historical data for better performance
        if initial_stocks:
            self._prefetch_historical_data(initial_stocks)
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self.add_stock, ticker, details['shares'], details['purchase_date']): ticker 
                           for ticker, details in initial_stocks.items()}
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error adding {futures[future]}: {e}")
        print("Portfolio initialized successfully!")

    @lru_cache(maxsize=365)  # Cache trading day calculations
    def _get_nearest_trading_day(self, date):
        """Adjusts for weekends/holidays by finding the last available trading day."""
        while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            date -= timedelta(days=1)
        return date

    def _fetch_polygon_price(self, ticker, date):
        """Fetch stock price from Polygon API."""
        date = self._get_nearest_trading_day(date)
        date_str = date.strftime('%Y-%m-%d')
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date_str}/{date_str}?apiKey={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if "results" in data and data["results"]:
                return data["results"][0]["c"]
        except Exception as e:
            print(f"Polygon API error for {ticker} on {date_str}: {e}")
        return None

    def _fetch_yahoo_prices(self, tickers, start_date, end_date):
        """Batch fetch stock prices from Yahoo Finance."""
        try:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)
            if isinstance(data, pd.DataFrame) and 'Adj Close' in data:
                return data['Adj Close']
        except Exception as e:
            print(f"Yahoo Finance batch fetch error: {e}")
        return None

    def get_stock_price(self, ticker, date):
        """Get stock price, prioritizing Polygon API with Yahoo Finance as a fallback."""
        date = self._get_nearest_trading_day(date)
        date_str = date.strftime('%Y-%m-%d')
        cache_key = (ticker, date_str)

        if cache_key in self.price_cache:
            return self.price_cache[cache_key]

        price = self._fetch_polygon_price(ticker, date)
        if price is None:
            print(f"Falling back to Yahoo Finance for {ticker} on {date_str}...")
            price = self._fetch_yahoo_prices([ticker], date - timedelta(days=5), date + timedelta(days=5))
            if price is not None and ticker in price:
                price = price.loc[price.index.get_loc(date, method='nearest')]

        if price is not None:
            self.price_cache[cache_key] = price
        return price

    def _prefetch_historical_data(self, stocks):
        """Batch prefetch historical stock data from Yahoo and Polygon APIs."""
        tickers = list(stocks.keys())
        start_date = min(details['purchase_date'] for details in stocks.values()).strftime('%Y-%m-%d')
        end_date = datetime.today().strftime('%Y-%m-%d')

        # Batch request from Yahoo Finance
        yahoo_data = self._fetch_yahoo_prices(tickers, start_date, end_date)
        if yahoo_data is not None:
            for ticker in tickers:
                if ticker in yahoo_data:
                    for date, price in yahoo_data[ticker].items():
                        self.price_cache[(ticker, date.strftime('%Y-%m-%d'))] = price

        # Parallel Polygon API fetching
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._fetch_polygon_price, ticker, datetime.strptime(start_date, '%Y-%m-%d')): ticker 
                       for ticker in tickers}
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    price = future.result()
                    if price is not None:
                        self.price_cache[(ticker, start_date)] = price
                except Exception as e:
                    print(f"Polygon API fetch error for {ticker}: {e}")

    def add_stock(self, ticker, shares, purchase_date):
        """Add a stock with optimized batch fetching."""
        purchase_date = self._get_nearest_trading_day(purchase_date)
        if purchase_date > datetime.today():
            raise ValueError(f"Purchase date {purchase_date.strftime('%Y-%m-%d')} is in the future.")

        purchase_price = self.get_stock_price(ticker, purchase_date)
        if purchase_price is None:
            raise ValueError(f"Could not fetch price data for {ticker} on {purchase_date.strftime('%Y-%m-%d')}")

        if ticker in self.stocks:
            total_shares = self.stocks[ticker]['shares'] + shares
            total_cost = (self.stocks[ticker]['shares'] * self.stocks[ticker]['purchase_price'] + 
                          shares * purchase_price)
            avg_price = total_cost / total_shares
            self.stocks[ticker]['shares'] = total_shares
            self.stocks[ticker]['purchase_price'] = avg_price
        else:
            self.stocks[ticker] = {'shares': shares, 'purchase_date': purchase_date, 'purchase_price': purchase_price}

    def get_total_value(self, date=None):
        """Calculate total portfolio value using parallel processing."""
        if date is None:
            date = datetime.today()

        total_value = 0
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.get_stock_price, ticker, date): ticker for ticker in self.stocks}
            for future in as_completed(futures):
                price = future.result()
                if price is not None:
                    total_value += price * self.stocks[futures[future]]['shares']

        return total_value

    def display_portfolio(self):
        """Display current portfolio status."""
        print("\nCurrent Portfolio Status:")
        print("-" * 80)
        print(f"{'Ticker':<8} {'Shares':<8} {'Buy Price':<12} {'Curr Price':<12} {'Total Value':<12} {'Change %':<10}")
        print("-" * 80)

        total_value = 0
        total_cost = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.get_stock_price, ticker, datetime.today()): ticker for ticker in self.stocks}
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    current_price = future.result()
                    if current_price is None:
                        continue
                    shares = self.stocks[ticker]['shares']
                    value = current_price * shares
                    cost = self.stocks[ticker]['purchase_price'] * shares
                    change = (current_price - self.stocks[ticker]['purchase_price']) / self.stocks[ticker]['purchase_price'] * 100
                    total_value += value
                    total_cost += cost
                    print(f"{ticker:<8} {shares:<8} ${self.stocks[ticker]['purchase_price']:<11.2f} ${current_price:<11.2f} ${value:<11.2f} {change:>7.2f}%")
                except Exception as e:
                    print(f"Error fetching data for {ticker}: {e}")

        print("-" * 80)
        total_return = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        print(f"Total Cost: ${total_cost:.2f}")
        print(f"Total Value: ${total_value:.2f}")
        print(f"Total Return: {total_return:.2f}%")



    def display_yearly_values(self):
        """Display portfolio value at the end of each year."""
        print("\nYearly Portfolio Values:")
        print("-" * 50)
        print(f"{'Year':<10} {'Value':<15} {'Change %':<10}")
        print("-" * 50)
        
        start_year = min(data['purchase_date'].year for data in self.stocks.values())
        end_year = datetime.today().year
        previous_value = None
        
        for year in range(start_year, end_year + 1):
            year_end = datetime(year, 12, 31)
            if year == datetime.today().year:
                year_end = datetime.today()
            
            value = self.get_total_value(year_end)
            
            if previous_value is not None and previous_value != 0:
                change = ((value - previous_value) / previous_value * 100)
                print(f"{year:<10} ${value:<14.2f} {change:>7.2f}%")
            else:
                print(f"{year:<10} ${value:<14.2f} {'N/A':>7}")
            
            previous_value = value

    def plot_portfolio_value(self):
        """Plot portfolio value over time with improved error handling."""
        if not self.stocks:
            print("No stocks in portfolio to plot.")
            return

        start_date = min(data['purchase_date'] for data in self.stocks.values())
        end_date = datetime.today()
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days only

        portfolio_values = []
        for date in dates:
            total_value = self.get_total_value(date)
            portfolio_values.append(total_value)


        
        ut.plot_portfolio_value(dates, portfolio_values)
        