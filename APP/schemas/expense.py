from pydantic import BaseModel
from datetime import date

# 這是新增記帳時用的 (目前前端還沒做手動選收入，先預設 expense 或選填)
class ExpenseCreate(BaseModel):
    amount: int
    category: str
    description: str | None = None
    date: date
    record_type: str = "expense" 

# 這是回傳給前端顯示用的
class ExpenseResponse(BaseModel):
    id: int
    amount: int
    category: str
    description: str | None = None
    date: date
    record_type: str 
    
    class Config:
        from_attributes = True