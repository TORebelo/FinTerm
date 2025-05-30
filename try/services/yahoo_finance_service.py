import asyncio
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
import pytz
from concurrent.futures import ThreadPoolExecutor
from core.http_client import HttpClient
from models.stock_models import StockQuote, StockInfo, ChartData

class YahooFinanceService:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        self.thread_pool = ThreadPoolExecutor(max_workers=5)

    async def _run_in_executor(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args)

    async def get_stock_quote(self, ticker: str) -> Optional[StockQuote]:
        """Get stock quote from Yahoo Finance API"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            data = await self.http_client.make_request(url)
            
            if not data or not data.get("chart", {}).get("result"):
                return None
                
            result = data["chart"]["result"][0]
            meta = result["meta"]
            
            current_price = meta.get("regularMarketPrice", 0)
            previous_close = meta.get("previousClose", 0)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            return StockQuote(
                symbol=ticker.upper(),
                price=current_price,
                change=change,
                changePercent=change_percent,
                volume=meta.get("regularMarketVolume", 0),
                previousClose=previous_close
            )
        except Exception as e:
            print(f"Yahoo Finance quote error for {ticker}: {e}")
            return None

    async def get_stock_info(self, ticker: str) -> Optional[StockInfo]:
        """Get comprehensive stock information"""
        try:
            # Fetch both quote and summary data
            quote_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            summary_url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=summaryDetail,defaultKeyStatistics,assetProfile"
            
            quote_data, summary_data = await asyncio.gather(
                self.http_client.make_request(quote_url),
                self.http_client.make_request(summary_url)
            )
            
            if not quote_data or not summary_data:
                return None
                
            result = quote_data["chart"]["result"][0]
            meta = result["meta"]
            summary = summary_data["quoteSummary"]["result"][0]
            
            summary_detail = summary.get("summaryDetail", {})
            key_stats = summary.get("defaultKeyStatistics", {})
            profile = summary.get("assetProfile", {})
            
            current_price = meta.get("regularMarketPrice", 0)
            previous_close = meta.get("previousClose", 0)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            return StockInfo(
                symbol=ticker.upper(),
                name=meta.get("longName", ticker.upper()),
                price=current_price,
                change=change,
                changePercent=change_percent,
                volume=meta.get("regularMarketVolume", 0),
                previousClose=previous_close,
                marketCap=summary_detail.get("marketCap", {}).get("raw", 0),
                peRatio=summary_detail.get("trailingPE", {}).get("raw", 0),
                eps=key_stats.get("trailingEps", {}).get("raw", 0),
                high52w=summary_detail.get("fiftyTwoWeekHigh", {}).get("raw", 0),
                low52w=summary_detail.get("fiftyTwoWeekLow", {}).get("raw", 0),
                dividendYield=summary_detail.get("dividendYield", {}).get("raw", 0) * 100,
                beta=key_stats.get("beta", {}).get("raw", 0),
                sector=profile.get("sector", "N/A"),
                industry=profile.get("industry", "N/A")
            )
        except Exception as e:
            print(f"Yahoo Finance info error for {ticker}: {e}")
            return None

    async def get_chart_data(self, ticker: str, period: str = "1mo") -> List[ChartData]:
        """Get chart data from Yahoo Finance"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={period}&interval=1d"
            data = await self.http_client.make_request(url)
            
            if not data or not data.get("chart", {}).get("result"):
                return []
                
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            quotes = result.get("indicators", {}).get("quote", [{}])[0]
            
            chart_data = []
            for i, timestamp in enumerate(timestamps):
                if i < len(quotes.get("close", [])) and quotes["close"][i]:
                    chart_data.append(ChartData(
                        date=datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                        open=quotes.get("open", [])[i] or 0,
                        high=quotes.get("high", [])[i] or 0,
                        low=quotes.get("low", [])[i] or 0,
                        close=quotes.get("close", [])[i] or 0,
                        volume=quotes.get("volume", [])[i] or 0
                    ))
            
            return chart_data
        except Exception as e:
            print(f"Yahoo Finance chart error for {ticker}: {e}")
            return []
