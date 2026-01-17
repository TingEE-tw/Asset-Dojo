from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BudgetCreate(BaseModel):
    amount: int

class BudgetResponse(BaseModel):
    amount: int
    updated_at: datetime
    can_update: bool          # 告訴前端能不能改
    next_update_date: Optional[datetime] = None # 如果不能改，什麼時候解鎖？

    class Config:
        from_attributes = True