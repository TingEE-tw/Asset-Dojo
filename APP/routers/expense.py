from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from APP.database import get_db
from APP import models
from APP.schemas.expense import ExpenseCreate, ExpenseResponse, AnnualSummary
from typing import List
from datetime import date, datetime, timedelta

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

# --- 年度損益分析 (只抓近 3 年) ---
@router.get("/annual_summary", response_model=List[AnnualSummary])
def get_annual_summary(db: Session = Depends(get_db)):
    # 1. 計算年份範圍 (今年, 去年, 前年)
    current_year = date.today().year
    start_year = current_year - 2
    
    # 2. 利用 SQL 聚合查詢：按年份與類型加總
    # SELECT year, record_type, SUM(amount) ...
    results = db.query(
        extract('year', models.Expense.date).label('year'),
        models.Expense.record_type,
        func.sum(models.Expense.amount).label('total')
    ).filter(
        extract('year', models.Expense.date) >= start_year
    ).group_by(
        'year', models.Expense.record_type
    ).all()
    
    # 3. 整理數據結構
    # 格式轉變: {2024: {'income': 100, 'expense': 50}, 2025: ...}
    data_map = {}
    for r in results:
        y = int(r.year)
        if y not in data_map:
            data_map[y] = {"income": 0, "expense": 0}
        
        # r.record_type 可能是 'income' 或 'expense'
        # r.total 是總金額
        if r.record_type == "income":
            data_map[y]["income"] = r.total
        elif r.record_type == "expense":
            data_map[y]["expense"] = r.total

    # 4. 計算損益與成長率
    summary_list = []
    years = sorted(data_map.keys()) # 確保由舊到新排序 (方便算成長率)
    
    previous_profit = None # 用來記上一年的獲利 (算 YoY 用)

    for y in years:
        inc = data_map[y]["income"]
        exp = data_map[y]["expense"]
        profit = inc - exp
        
        # 計算成長率
        growth = None
        if previous_profit is not None and previous_profit != 0:
            growth = ((profit - previous_profit) / abs(previous_profit)) * 100
        
        summary_list.append(AnnualSummary(
            year=y,
            total_income=inc,
            total_expense=exp,
            net_profit=profit,
            growth_pct=growth
        ))
        
        # 更新 previous_profit 給下一輪用
        previous_profit = profit

    # 回傳前反轉列表，讓最新的年份排在最上面 (符合閱讀習慣)
    return summary_list[::-1]