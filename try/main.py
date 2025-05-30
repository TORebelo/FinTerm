from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import stock_router, portfolio_router
from core.http_client import HttpClient
from services.yahoo_finance_service import YahooFinanceService
from services.polygon_service import PolygonService
from services.sec_service import SECService
from portfolio.portfolio_manager import PortfolioManager
from config import settings

app = FastAPI(title="Stock Terminal API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
http_client = HttpClient()
yahoo_service = YahooFinanceService(http_client)
polygon_service = PolygonService(http_client)
sec_service = SECService(http_client)
portfolio_manager = PortfolioManager(yahoo_service, polygon_service)

# Include routers
app.include_router(stock_router.router)
app.include_router(portfolio_router.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

# Keep legacy endpoints for backward compatibility
@app.get("/api/quote/{ticker}")
async def get_quote(ticker: str):
    """Legacy endpoint - redirects to new router"""
    from routers.stock_router import get_stock_quote
    return await get_stock_quote(ticker)

@app.get("/api/stock/{ticker}")
async def get_stock_info(ticker: str):
    """Legacy endpoint - redirects to new router"""
    from routers.stock_router import get_stock_info
    return await get_stock_info(ticker)

@app.get("/api/chart/{ticker}")
async def get_chart_data(ticker: str, period: str = "1mo"):
    """Legacy endpoint - redirects to new router"""
    from routers.stock_router import get_chart_data
    return await get_chart_data(ticker, period)

@app.get("/api/portfolio")
async def get_portfolio():
    """Legacy endpoint - redirects to new router"""
    from routers.portfolio_router import get_portfolio_summary
    return await get_portfolio_summary()

@app.post("/api/portfolio")
async def add_to_portfolio(symbol: str, shares: int, price: float):
    """Legacy endpoint - redirects to new router"""
    from routers.portfolio_router import add_stock_to_portfolio
    from models.portfolio_models import StockPurchaseInfo
    from datetime import datetime
    
    stock_info = StockPurchaseInfo(
        ticker=symbol,
        shares=shares,
        purchase_price=price,
        purchase_date=datetime.now()
    )
    return await add_stock_to_portfolio(stock_info)

@app.get("/api/news")
async def get_market_news():
    """Get market news"""
    from datetime import datetime, timedelta
    news = [
        {
            "title": "Federal Reserve Signals Potential Rate Cut in Q2",
            "summary": "The Federal Reserve indicated in today's meeting that economic conditions may warrant a rate reduction in the second quarter.",
            "url": "https://example.com/news/1",
            "publishedAt": datetime.now().isoformat(),
            "source": "Financial Times",
            "sentiment": "positive"
        },
        {
            "title": "Tech Stocks Rally on AI Breakthrough Announcements",
            "summary": "Major technology companies saw significant gains following announcements of new artificial intelligence capabilities.",
            "url": "https://example.com/news/2",
            "publishedAt": (datetime.now() - timedelta(hours=1)).isoformat(),
            "source": "Reuters",
            "sentiment": "positive"
        },
        {
            "title": "Energy Sector Faces Headwinds Amid Regulatory Changes",
            "summary": "New environmental regulations are expected to impact energy companies' operations and profitability in the coming quarters.",
            "url": "https://example.com/news/3",
            "publishedAt": (datetime.now() - timedelta(hours=2)).isoformat(),
            "source": "Bloomberg",
            "sentiment": "negative"
        },
        {
            "title": "Consumer Spending Data Shows Mixed Signals",
            "summary": "Latest consumer spending reports indicate varied performance across different sectors, with retail showing strength while services lag.",
            "url": "https://example.com/news/4",
            "publishedAt": (datetime.now() - timedelta(hours=3)).isoformat(),
            "source": "Wall Street Journal",
            "sentiment": "neutral"
        },
        {
            "title": "Cryptocurrency Market Stabilizes After Recent Volatility",
            "summary": "Digital assets are showing signs of stabilization following a period of high volatility, with institutional adoption continuing to grow.",
            "url": "https://example.com/news/5",
            "publishedAt": (datetime.now() - timedelta(hours=4)).isoformat(),
            "source": "CoinDesk",
            "sentiment": "neutral"
        }
    ]
    return {"articles": news}

@app.on_event("startup")
async def startup_event():
    print("Stock Terminal API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.close()
    print("Stock Terminal API shutting down...")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
