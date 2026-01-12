from pydantic import BaseModel
from typing import Optional

class StockCreate(BaseModel):
    symbol: str
    shares: int
    price: float

# --- 升級後的 Response ---
class StockResponse(BaseModel):
    id: int
    symbol: str
    shares: int
    average_cost: float
    
    # 新增這三個「計算欄位」
    current_price: Optional[float] = 0.0  # 現價
    market_value: Optional[float] = 0.0   # 市值 (現價 * 股數)
    profit: Optional[float] = 0.0         # 損益 (市值 - 成本)

    class Config:
        from_attributes = True