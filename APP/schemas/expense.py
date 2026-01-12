from pydantic import BaseModel
from datetime import date
from typing import Optional

# 這是「接收」資料用的模型 (使用者填寫)
class ExpenseCreate(BaseModel):
    amount: int
    category: str
    description: Optional[str] = None
    date: date

# 這是「回傳」給前端用的模型 (包含 ID 和建立時間)
class ExpenseResponse(ExpenseCreate):
    id: int
    
    class Config:
        from_attributes = True # 讓 Pydantic 能夠讀取 SQLAlchemy 的資料