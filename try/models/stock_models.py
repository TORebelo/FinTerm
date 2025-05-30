from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class StockQuote(BaseModel):
    symbol: str
    price: float
    change: float
    changePercent: float
    volume: int
    previousClose: float

class StockDetails(BaseModel):
    ticker: str
    company_name: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    current_price: Optional[float] = None

class SECFiling(BaseModel):
    formType: str
    filedDate: str
    reportDate: Optional[str] = None
    url: str
    accessionNumber: Optional[str] = None

class StockInfoResponse(BaseModel):
    general_information: Optional[StockDetails] = None
    market_data: Optional[Dict[str, Any]] = None
    financial_metrics: Optional[Dict[str, Any]] = None
    recent_sec_filings: Optional[List[SECFiling]] = []
    chart_json: Optional[Dict[str, Any]] = None

class StockInfo(StockQuote):
    name: str
    marketCap: float
    peRatio: float
    eps: float
    high52w: float
    low52w: float
    dividendYield: float
    beta: float
    sector: str
    industry: str

class ChartData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class PortfolioHolding(BaseModel):
    symbol: str
    shares: int
    avgCost: float
    currentPrice: float
    totalValue: float
    gainLoss: float
    gainLossPercent: float

class PortfolioSummary(BaseModel):
    holdings: List[PortfolioHolding]
    totalValue: float
    totalCost: float
    totalGainLoss: float
    totalGainLossPercent: float
