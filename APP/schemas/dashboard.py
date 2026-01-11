from pydantic import BaseModel
from typing import List

# 定義這是一個「預算」的資料格式
class BudgetInfo(BaseModel):
    total: float
    spent: float
    remaining: float

# 定義這是一個「股票」的簡易格式
class StockSummary(BaseModel):
    total_value: float
    profit: float
    profit_percent: float

# 定義整個「儀表板」的回傳格式
class DashboardResponse(BaseModel):
    budget: BudgetInfo
    daily_trend: List[float]
    stock: StockSummary