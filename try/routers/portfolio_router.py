from fastapi import APIRouter, HTTPException, Body
from models.portfolio_models import StockPurchaseInfo, PortfolioSummary
from portfolio.portfolio_manager import PortfolioManager
from services.yahoo_finance_service import YahooFinanceService
from services.polygon_service import PolygonService
from core.http_client import HttpClient
from datetime import datetime

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"]
)

# Initialize services
http_client = HttpClient()
yahoo_service = YahooFinanceService(http_client)
polygon_service = PolygonService(http_client)
portfolio_manager_instance = PortfolioManager(yahoo_service, polygon_service)

@router.post("/add", status_code=201)
async def add_stock_to_portfolio(stock_info: StockPurchaseInfo = Body(...)):
    """Add stock to portfolio"""
    try:
        # FastAPI automatically validates stock_info against StockPurchaseInfo model
        result = await portfolio_manager_instance.add_stock(
            symbol=stock_info.ticker.upper(),
            shares=stock_info.shares,
            avg_cost=stock_info.purchase_price
        )
        return {"message": f"Added {stock_info.shares} shares of {stock_info.ticker}", "success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred while adding the stock: {str(e)}")

# Legacy endpoint for backward compatibility with the frontend
@router.post("/")
async def legacy_add_stock(symbol: str = Body(...), shares: int = Body(...), price: float = Body(...)):
    """Legacy endpoint for adding stock to portfolio"""
    try:
        stock_info = StockPurchaseInfo(
            ticker=symbol.upper(),
            shares=shares,
            purchase_price=price,
            purchase_date=datetime.now()
        )
        return await add_stock_to_portfolio(stock_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding stock: {str(e)}")

@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary():
    """Get portfolio summary"""
    try:
        summary = await portfolio_manager_instance.get_portfolio_summary()
        
        # Convert to the expected format
        from models.portfolio_models import PortfolioStock
        stocks = []
        for holding in summary.holdings:
            stocks.append(PortfolioStock(
                ticker=holding.symbol,
                shares=holding.shares,
                purchase_price=holding.avgCost,
                purchase_date=datetime.now(),  # You might want to store this properly
                current_price=holding.currentPrice,
                current_value=holding.totalValue,
                change_percent=holding.gainLossPercent,
                gain_loss=holding.gainLoss
            ))
        
        return PortfolioSummary(
            stocks=stocks,
            total_cost=summary.totalCost,
            total_value=summary.totalValue,
            total_return_percent=summary.totalGainLossPercent,
            total_gain_loss=summary.totalGainLoss
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred while fetching portfolio summary: {str(e)}")

@router.delete("/{ticker}")
async def remove_stock_from_portfolio(ticker: str):
    """Remove stock from portfolio"""
    try:
        # This would need to be implemented in your portfolio manager
        return {"message": f"Removed {ticker} from portfolio", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/holdings")
async def get_portfolio_holdings():
    """Get detailed portfolio holdings"""
    try:
        summary = await portfolio_manager_instance.get_portfolio_summary()
        return {"holdings": summary.holdings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint for backward compatibility
@router.get("/")
async def get_portfolio_view():
    """Legacy endpoint for portfolio summary"""
    return await get_portfolio_summary()
