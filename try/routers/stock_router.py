from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import asyncio
import json
import plotly.graph_objs as go
import yfinance as yf
import pandas as pd

from services.yahoo_finance_service import YahooFinanceService
from services.polygon_service import PolygonService
from services.sec_service import SECService
from models.stock_models import StockInfoResponse, StockDetails, SECFiling, StockQuote, StockInfo, ChartData
from core.http_client import HttpClient
from config import settings

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"]
)

# Initialize services
http_client = HttpClient()
yahoo_service = YahooFinanceService(http_client)
polygon_service = PolygonService(http_client)
sec_service = SECService(http_client)

@router.get("/{ticker}/info", response_model=StockInfoResponse)
async def get_full_stock_info(ticker: str):
    """Get comprehensive stock information with chart data"""
    try:
        # Concurrently fetch all data
        yf_info_task = yahoo_service.get_stock_info(ticker)
        polygon_details_task = polygon_service.get_ticker_details(ticker)
        sec_filings_task = sec_service.get_stock_sec_filings(ticker, count=3)
        
        # Chart data using yfinance in executor
        chart_json_task = yahoo_service._run_in_executor(
            lambda t: yf.Ticker(t).history(period="1y"), ticker
        )

        yf_info, polygon_details, sec_data, chart_history_df = await asyncio.gather(
            yf_info_task, polygon_details_task, sec_filings_task, chart_json_task
        )

        if not yf_info and not polygon_details:
            raise HTTPException(status_code=404, detail=f"Could not retrieve sufficient info for ticker {ticker}")

        # Combine data into StockInfoResponse
        general_info = StockDetails(ticker=ticker)
        market_data = {}
        financial_metrics = {}
        
        if yf_info:
            general_info.company_name = yf_info.name
            general_info.industry = yf_info.industry
            general_info.sector = yf_info.sector
            general_info.current_price = yf_info.price
            
            market_data = {
                "market_cap": yf_info.marketCap,
                "volume": yf_info.volume,
                "high_52w": yf_info.high52w,
                "low_52w": yf_info.low52w,
                "previous_close": yf_info.previousClose
            }
            
            financial_metrics = {
                "pe_ratio": yf_info.peRatio,
                "eps": yf_info.eps,
                "beta": yf_info.beta,
                "dividend_yield": yf_info.dividendYield
            }

        # SEC Filings
        filings_models = []
        if sec_data:
            for filing in sec_data:
                if "error" not in filing:
                    filings_models.append(SECFiling(
                        formType=filing.get("formType", ""),
                        filedDate=filing.get("filedDate", ""),
                        reportDate=filing.get("reportDate"),
                        url=filing.get("url", ""),
                        accessionNumber=filing.get("accessionNumber")
                    ))

        # Chart (Plotly to JSON)
        plotly_chart_json = None
        if isinstance(chart_history_df, pd.DataFrame) and not chart_history_df.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=chart_history_df.index,
                open=chart_history_df['Open'],
                high=chart_history_df['High'],
                low=chart_history_df['Low'],
                close=chart_history_df['Close']
            )])
            fig.update_layout(title=f"{ticker.upper()} Stock Chart")
            plotly_chart_json = json.loads(fig.to_json())

        return StockInfoResponse(
            general_information=general_info,
            market_data=market_data,
            financial_metrics=financial_metrics,
            recent_sec_filings=filings_models,
            chart_json=plotly_chart_json
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock info: {str(e)}")

@router.get("/{ticker}/quote", response_model=StockQuote)
async def get_stock_quote(ticker: str):
    """Get stock quote with fallback sources"""
    try:
        # Try Yahoo Finance first
        quote = await yahoo_service.get_stock_quote(ticker)
        if quote:
            return quote
        
        # Fallback to Polygon
        quote = await polygon_service.get_stock_quote(ticker)
        if quote:
            return quote
            
        raise HTTPException(status_code=404, detail=f"Quote not found for {ticker}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/chart")
async def get_chart_data(ticker: str, period: str = Query("1mo", description="Chart period")):
    """Get chart data for stock"""
    try:
        # First try Yahoo Finance
        data = await yahoo_service.get_chart_data(ticker, period)
        if not data:  # Fallback to direct yfinance if empty
            history = yf.Ticker(ticker).history(period=period)
            if not history.empty:
                data = history.reset_index().to_dict("records")
        
        if not data:
            raise HTTPException(status_code=404, detail="No chart data available")
            
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{ticker}/sec")
async def get_sec_filings(ticker: str, count: int = Query(5, description="Number of filings to return")):
    """Get SEC filings for ticker"""
    try:
        filings = await sec_service.get_stock_sec_filings(ticker, count=count)
        return {"filings": filings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoints for backward compatibility
@router.get("/{ticker}")
async def get_stock_info(ticker: str):
    """Legacy endpoint for stock info"""
    try:
        info = await yahoo_service.get_stock_info(ticker)
        if not info:
            raise HTTPException(status_code=404, detail=f"Stock info not found for {ticker}")
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
