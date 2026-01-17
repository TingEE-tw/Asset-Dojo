from pydantic import BaseModel
from typing import Optional

# --- 1. 買入相關 ---
class StockCreate(BaseModel):
    symbol: str   
    shares: int   
    price: float  

class StockResponse(BaseModel):
    id: int
    symbol: str
    shares: int
    average_cost: float
    
    # 這些是後來加的計算欄位
    current_price: Optional[float] = 0.0
    market_value: Optional[float] = 0.0
    profit: Optional[float] = 0.0

    class Config:
        from_attributes = True

# --- 2. 賣出相關 ---
class StockSell(BaseModel):
    shares: int   # 賣出股數
    price: float  # 賣出價格

class StockSellResponse(BaseModel):
    symbol: str
    sold_shares: int
    realized_profit: float  # 實現損益