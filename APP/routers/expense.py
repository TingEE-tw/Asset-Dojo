from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from APP.database import get_db
from APP import models
from APP.schemas.expense import ExpenseCreate, ExpenseResponse
from typing import List
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses (記帳功能)"]
)

# 新增一筆支出
@router.post("/", response_model=ExpenseResponse)
def create_expense(expense_data: ExpenseCreate, db: Session = Depends(get_db)):
    # 1. 把 Pydantic 資料轉換成 SQLAlchemy 模型
    new_expense = models.Expense(
        amount=expense_data.amount,
        category=expense_data.category,
        description=expense_data.description,
        date=expense_data.date
    )
    
    # 2. 加入資料庫並存檔
    db.add(new_expense)
    db.commit()
    
    # 3. 重新整理 (拿回自動產生的 ID)
    db.refresh(new_expense)
    
    return new_expense

# 取得所有支出
@router.get("/", response_model=List[ExpenseResponse])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    #這行翻譯成 SQL 就是: SELECT * FROM expenses LIMIT 100 OFFSET 0;
    expenses = db.query(models.Expense).offset(skip).limit(limit).all()
    return expenses

# 刪除支出
@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    # 1. 尋找該筆紀錄
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    
    # 2. 如果找不到，回傳 404
    if not expense:
        raise HTTPException(status_code=404, detail="找不到這筆紀錄")

    # --- 3. 新增守門員：檢查是否超過 12 小時 ---
    if expense.created_at:
        # 計算時間差：現在時間 - 建立時間
        time_diff = datetime.now() - expense.created_at
        
        # 設定時限：12 小時
        limit = timedelta(hours=12)
        
        # 測試功能 : 10 秒
        #limit = timedelta(seconds=10)

        if time_diff > limit:
            # 超過時間，拒絕刪除 (回傳 400 Bad Request)
            raise HTTPException(
                status_code=400, 
                detail=f"🔒 此紀錄已超過 12 小時，無法刪除 (歷史帳務已鎖定)"
            )

    # 4. 通過檢查，執行刪除
    db.delete(expense)
    db.commit()
    
    return None