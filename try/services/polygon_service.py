from datetime import datetime
from typing import Optional, Dict, Any
from core.http_client import HttpClient
from models.stock_models import StockQuote
from config import settings

class PolygonService:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        self.base_url = "https://api.polygon.io"

    async def get_stock_quote(self, ticker: str) -> Optional[StockQuote]:
        """Get stock quote from Polygon.io"""
        try:
            url = f"{self.base_url}/v2/last/trade/{ticker.upper()}"
            params = {"apiKey": settings.POLYGON_API_KEY}
            
            data = await self.http_client.make_request(url, params=params)
            
            if not data or not data.get("results"):
                return None
                
            result = data["results"]
            # Note: Polygon's last trade endpoint doesn't provide all quote data
            # This is a simplified implementation
            
            return StockQuote(
                symbol=ticker.upper(),
                price=result.get("p", 0),
                change=0,  # Would need additional API call
                changePercent=0,  # Would need additional API call
                volume=result.get("s", 0),
                previousClose=0  # Would need additional API call
            )
        except Exception as e:
            print(f"Polygon quote error for {ticker}: {e}")
            return None

    async def get_daily_stock_price(self, ticker: str, date: datetime) -> Optional[float]:
        """Get historical stock price for specific date"""
        try:
            date_str = date.strftime('%Y-%m-%d')
            url = f"{self.base_url}/v2/aggs/ticker/{ticker.upper()}/range/1/day/{date_str}/{date_str}"
            params = {"adjusted": "true", "apiKey": settings.POLYGON_API_KEY}
            
            data = await self.http_client.make_request(url, params=params)
            
            if data and data.get("results") and len(data["results"]) > 0:
                return data["results"][0].get("c")  # Closing price
                
        except Exception as e:
            print(f"Polygon price error for {ticker} on {date_str}: {e}")
            
        return None

    async def get_ticker_details(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get ticker details from Polygon.io"""
        try:
            url = f"{self.base_url}/v3/reference/tickers/{ticker.upper()}"
            params = {"apiKey": settings.POLYGON_API_KEY}
            
            data = await self.http_client.make_request(url, params=params)
            
            if data and data.get("results"):
                return data["results"]
                
        except Exception as e:
            print(f"Polygon ticker details error for {ticker}: {e}")
            
        return None
