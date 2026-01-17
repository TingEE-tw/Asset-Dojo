from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from APP.database import get_db
from APP import models
from APP.schemas.budget import BudgetCreate, BudgetResponse

router = APIRouter(
    prefix="/budget",
    tags=["budget"]
)

# 設定鎖定期限：90 天 (3個月)
LOCK_PERIOD_DAYS = 90

@router.get("/", response_model=BudgetResponse)
def get_budget(db: Session = Depends(get_db)):
    # 預設只有一筆預算設定 (單人使用)
    budget = db.query(models.Budget).first()
    
    if not budget:
        # 如果還沒設定過，回傳預設值 (0)，並且說是可設定的
        return BudgetResponse(
            amount=0, 
            updated_at=datetime.min, 
            can_update=True
        )

    # 檢查是否過期
    time_passed = datetime.now() - budget.updated_at
    is_locked = time_passed < timedelta(days=LOCK_PERIOD_DAYS)
    
    next_date = None
    if is_locked:
        next_date = budget.updated_at + timedelta(days=LOCK_PERIOD_DAYS)

    return BudgetResponse(
        amount=budget.monthly_limit,
        updated_at=budget.updated_at,
        can_update=not is_locked, # 如果還在鎖定中，can_update 就是 False
        next_update_date=next_date
    )

@router.post("/", response_model=BudgetResponse)
def set_budget(data: BudgetCreate, db: Session = Depends(get_db)):
    budget = db.query(models.Budget).first()

    # 1. 如果是第一次設定 -> 直接建立
    if not budget:
        new_budget = models.Budget(monthly_limit=data.amount, updated_at=datetime.now())
        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)
        return get_budget(db) # 重用上面的邏輯回傳

    # 2. 如果已經有設定 -> 檢查是否鎖定中
    time_passed = datetime.now() - budget.updated_at
    if time_passed < timedelta(days=LOCK_PERIOD_DAYS):
        # 計算還剩幾天
        days_left = LOCK_PERIOD_DAYS - time_passed.days
        raise HTTPException(
            status_code=400, 
            detail=f"🔒 預算修煉進行中！為了養成習慣，請堅持原本的設定。還有 {days_left} 天才能更改。"
        )

    # 3. 解鎖了 -> 更新預算與時間
    budget.monthly_limit = data.amount
    budget.updated_at = datetime.now() # 重置鎖定時間
    db.commit()
    
    return get_budget(db)