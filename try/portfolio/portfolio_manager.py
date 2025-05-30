from typing import Dict, Any, List
from datetime import datetime
import asyncio
from models.stock_models import PortfolioSummary, PortfolioHolding
from services.yahoo_finance_service import YahooFinanceService
from services.polygon_service import PolygonService

class PortfolioManager:
    def __init__(self, yahoo_service: YahooFinanceService, polygon_service: PolygonService):
        self.yahoo_service = yahoo_service
        self.polygon_service = polygon_service
        self.stocks: Dict[str, Dict[str, Any]] = {
            "AAPL": {"shares": 10, "avgCost": 150.0, "dateAdded": "2024-01-01"},
            "GOOGL": {"shares": 5, "avgCost": 2800.0, "dateAdded": "2024-01-15"},
            "MSFT": {"shares": 8, "avgCost": 380.0, "dateAdded": "2024-02-01"}
        }

    async def add_stock(self, symbol: str, shares: int, avg_cost: float):
        """Add stock to portfolio"""
        symbol = symbol.upper()
        
        if symbol in self.stocks:
            # Calculate new average cost
            existing = self.stocks[symbol]
            total_shares = existing["shares"] + shares
            total_cost = existing["shares"] * existing["avgCost"] + shares * avg_cost
            new_avg_cost = total_cost / total_shares
            
            self.stocks[symbol]["shares"] = total_shares
            self.stocks[symbol]["avgCost"] = new_avg_cost
        else:
            self.stocks[symbol] = {
                "shares": shares,
                "avgCost": avg_cost,
                "dateAdded": datetime.now().strftime("%Y-%m-%d")
            }

    async def get_portfolio_summary(self) -> PortfolioSummary:
        """Get portfolio summary with current prices"""
        if not self.stocks:
            return PortfolioSummary(
                holdings=[],
                totalValue=0,
                totalCost=0,
                totalGainLoss=0,
                totalGainLossPercent=0
            )

        holdings = []
        total_value = 0
        total_cost = 0

        # Fetch current prices for all holdings
        symbols = list(self.stocks.keys())
        price_tasks = [self.yahoo_service.get_stock_quote(symbol) for symbol in symbols]
        quotes = await asyncio.gather(*price_tasks)

        for i, symbol in enumerate(symbols):
            stock_data = self.stocks[symbol]
            quote = quotes[i]
            
            current_price = quote.price if quote else 0
            holding_value = current_price * stock_data["shares"]
            holding_cost = stock_data["avgCost"] * stock_data["shares"]
            gain_loss = holding_value - holding_cost
            gain_loss_percent = (gain_loss / holding_cost * 100) if holding_cost > 0 else 0

            holdings.append(PortfolioHolding(
                symbol=symbol,
                shares=stock_data["shares"],
                avgCost=stock_data["avgCost"],
                currentPrice=current_price,
                totalValue=holding_value,
                gainLoss=gain_loss,
                gainLossPercent=gain_loss_percent
            ))

            total_value += holding_value
            total_cost += holding_cost

        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

        return PortfolioSummary(
            holdings=holdings,
            totalValue=total_value,
            totalCost=total_cost,
            totalGainLoss=total_gain_loss,
            totalGainLossPercent=total_gain_loss_percent
        )
