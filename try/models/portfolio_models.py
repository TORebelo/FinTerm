from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StockPurchaseInfo(BaseModel):
    ticker: str
    shares: int
    purchase_price: float
    purchase_date: datetime

class PortfolioStock(BaseModel):
    ticker: str
    shares: int
    purchase_price: float
    purchase_date: datetime
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    change_percent: Optional[float] = None
    gain_loss: Optional[float] = None

class PortfolioSummary(BaseModel):
    stocks: List[PortfolioStock]
    total_cost: float
    total_value: float
    total_return_percent: float
    total_gain_loss: float
