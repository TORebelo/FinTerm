import asyncio
import aiohttp
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import concurrent.futures
import pytz

class Portfolio:
    def __init__(self, api_key: str, initial_stocks: Optional[Dict[str, Dict[str, Any]]] = None):
        self.api_key = api_key
        self.stocks: Dict[str, Dict[str, Any]] = {}
        self.price_cache: Dict[tuple, float] = {}
        self.retry_delay = 1  # Delay between API calls in seconds
        self.use_polygon = True  # Flag to alternate between Polygon and Yahoo Finance

        if initial_stocks:
            for ticker, details in initial_stocks.items():
                self.add_stock(ticker, details['shares'], details['purchase_date'])
        print("Portfolio initialized successfully!")

    @staticmethod
    def get_previous_trading_day(date: datetime) -> datetime:
        """Finds the previous trading day."""
        current_date = date
        while current_date.weekday() > 4:  # Skip weekends
            current_date -= timedelta(days=1)
        return current_date
    
    

    async def get_stock_price(self, ticker: str, date: datetime) -> Optional[float]:
        """Fetch stock price, alternating between Polygon.io and Yahoo Finance."""
        cache_key = (ticker, date.strftime('%Y-%m-%d'))
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]

        price = None
        if self.use_polygon:
            price = await self._fetch_from_polygon(ticker, date)
        else:
            price = await self._fetch_from_yahoo(ticker, date)

        self.use_polygon = not self.use_polygon  # Alternate for next call

        if price is not None:
            self.price_cache[cache_key] = price
            return price

        # If both methods fail, try previous trading day
        prev_day = self.get_previous_trading_day(date - timedelta(days=1))
        if prev_day < date - timedelta(days=10):  # Limit how far back we go
            return None
        return await self.get_stock_price(ticker, prev_day)

    async def _fetch_from_polygon(self, ticker: str, date: datetime) -> Optional[float]:
        """Fetch stock price from Polygon.io API."""
        date_str = date.strftime('%Y-%m-%d')
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date_str}/{date_str}?adjusted=true&apiKey={self.api_key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "results" in data and data["results"]:
                            return data["results"][0]["c"]
        except Exception as e:
            print(f"Error fetching from Polygon.io: {e}")

        await asyncio.sleep(self.retry_delay)  # Rate limiting
        return None


    async def _fetch_from_yahoo(self, ticker: str, date: datetime) -> Optional[float]:
        """Fetch stock price from Yahoo Finance."""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            try:
                stock = yf.Ticker(ticker)
                # Convert date to UTC timezone
                utc_date = date.replace(tzinfo=pytz.UTC)
                start_date = (utc_date - timedelta(days=5)).strftime('%Y-%m-%d')
                end_date = (utc_date + timedelta(days=1)).strftime('%Y-%m-%d')
                hist = await loop.run_in_executor(
                    pool,
                    lambda: stock.history(start=start_date, end=end_date)
                )

                if not hist.empty:
                    # Convert the index to UTC for comparison
                    hist.index = hist.index.tz_convert(pytz.UTC)
                    closest_date = min(hist.index, key=lambda x: abs(x - utc_date))
                    return hist.loc[closest_date, 'Close']
            except Exception as e:
                print(f"Error fetching from Yahoo Finance for {ticker} on {date}: {e}")
                import traceback
                traceback.print_exc()

        return None

    async def add_stock(self, ticker: str, shares: int, purchase_date: datetime):
        """Add a stock to the portfolio with improved error handling."""
        if purchase_date > datetime.today():
            raise ValueError(f"Purchase date {purchase_date.strftime('%Y-%m-%d')} is in the future.")

        purchase_price = await self.get_stock_price(ticker, purchase_date)
        if purchase_price is None:
            raise ValueError(f"Could not fetch price data for {ticker} around {purchase_date.strftime('%Y-%m-%d')}")

        if ticker in self.stocks:
            # Average out the purchase price if adding more shares
            total_shares = self.stocks[ticker]['shares'] + shares
            total_cost = (self.stocks[ticker]['shares'] * self.stocks[ticker]['purchase_price'] + 
                         shares * purchase_price)
            avg_price = total_cost / total_shares
            
            self.stocks[ticker]['shares'] = total_shares
            self.stocks[ticker]['purchase_price'] = avg_price
        else:
            self.stocks[ticker] = {
                'shares': shares,
                'purchase_date': purchase_date,
                'purchase_price': purchase_price
            }
        print(f"Added {shares} shares of {ticker} at ${purchase_price:.2f} per share")

    async def get_total_value(self, date: Optional[datetime] = None) -> float:
        """Get total portfolio value for a specific date."""
        if date is None:
            date = datetime.today()
        
        total_value = 0
        for ticker, data in self.stocks.items():
            if date >= data['purchase_date']:
                price = await self.get_stock_price(ticker, date)
                if price:
                    total_value += price * data['shares']
        return total_value

    async def display_portfolio(self):
        """Display portfolio with purchase prices and current values."""
        
        res = "\nCurrent Portfolio Status:"
        res += "\n" + "-" * 85 + "\n"
        res += f"{'Ticker':<8} {'Shares':<8} {'Buy Price':<12} {'Curr Price':<12} {'Total Value':<12} {'Change %':<10}\n"
        res += "-" * 85 + "\n"
       
        
        total_value = 0
        total_cost = 0
        for ticker, data in self.stocks.items():
            current_price = await self.get_stock_price(ticker, datetime.today())
            if current_price:
                value = current_price * data['shares']
                cost = data['purchase_price'] * data['shares']
                change = (current_price - data['purchase_price']) / data['purchase_price'] * 100
                total_value += value
                total_cost += cost
                res += f"{ticker:<8} {data['shares']:<8} ${data['purchase_price']:<11.2f} ${current_price:<11.2f} ${value:<11.2f} {change:>7.2f}%\n"
                
        
        res += "-" * 85 
        total_return = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        res += f"\nTotal Cost: ${total_cost:.2f}\n"
        res += f"Total Value: ${total_value:.2f}\n"
        res += f"Total Return: {total_return:.2f}%\n"
        print(res)
        return res
        

    async def display_yearly_values(self):
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
            
            value = await self.get_total_value(year_end)
            
            if previous_value is not None and previous_value != 0:
                change = ((value - previous_value) / previous_value * 100)
                print(f"{year:<10} ${value:<14.2f} {change:>7.2f}%")
            else:
                print(f"{year:<10} ${value:<14.2f} {'N/A':>7}")
            
            previous_value = value

    # Note: plot_portfolio_value method is omitted as it requires matplotlib,
    # which is not easily compatible with asyncio. Consider using an async-compatible
    # plotting library if needed.