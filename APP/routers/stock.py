from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import yfinance as yf  # <--- 引入抓股價神器
from APP.database import get_db
from APP import models
from APP.schemas.stock import StockCreate, StockResponse, StockSell, StockSellResponse
from datetime import date

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks (股票投資)"]
)

# 1. 買入股票 (維持不變)
@router.post("/", response_model=StockResponse)
def create_stock(stock_data: StockCreate, db: Session = Depends(get_db)):
    new_stock = models.Stock(
        symbol=stock_data.symbol,
        shares=stock_data.shares,
        average_cost=stock_data.price
    )
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock

# 2. 查詢庫存 (大幅升級！自動算損益)
@router.get("/", response_model=List[StockResponse])
def read_stocks(db: Session = Depends(get_db)):
    stocks = db.query(models.Stock).all()
    
    # 如果沒有股票，直接回傳空清單
    if not stocks:
        return []

    # --- 自動抓股價邏輯 ---
    results = []
    for stock in stocks:
        # 處理台股代號：如果是數字結尾 (如 2330)，要加上 ".TW" 才能讓 Yahoo 讀懂
        ticker = stock.symbol
        if ticker.isdigit(): 
            ticker = f"{ticker}.TW"
            
        try:
            # 去 Yahoo 抓最新價格
            # period="1d" 代表抓一天的資料
            data = yf.Ticker(ticker)
            history = data.history(period="1d")
            
            if not history.empty:
                # 拿到最新一筆收盤價
                current_price = history['Close'].iloc[-1]
            else:
                current_price = stock.average_cost # 抓不到就先用成本價代替
                
        except Exception:
            current_price = stock.average_cost # 網路錯誤也先用成本價

        # 開始計算
        market_value = current_price * stock.shares     # 市值
        total_cost = stock.average_cost * stock.shares  # 總成本
        profit = market_value - total_cost              # 賺賠金額

        # 整理資料回傳
        # 這裡我們不存入資料庫，只是「算」給前端看
        stock_data = StockResponse(
            id=stock.id,
            symbol=stock.symbol,
            shares=stock.shares,
            average_cost=stock.average_cost,
            current_price=round(current_price, 2),
            market_value=round(market_value, 0),
            profit=round(profit, 0)
        )
        results.append(stock_data)
        
    return results

# 3. 賣出股票 (維持不變)
@router.post("/{stock_id}/sell", response_model=StockSellResponse)
def sell_stock(stock_id: int, sell_data: StockSell, db: Session = Depends(get_db)):
    # 1. 找股票
    stock = db.query(models.Stock).filter(models.Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="找不到這檔股票")
    
    # 2. 檢查庫存
    if stock.shares < sell_data.shares:
        raise HTTPException(status_code=400, detail="庫存不足，無法賣出")

    # 3. 計算損益
    cost_basis = stock.average_cost * sell_data.shares # 這次賣出的成本
    revenue = sell_data.price * sell_data.shares       # 這次賣出的收入
    profit_loss = revenue - cost_basis                 # 賺或賠的錢

    # 4. 處理庫存
    stock.shares -= sell_data.shares
    if stock.shares == 0:
        db.delete(stock) # 賣光了就刪掉庫存紀錄

    # --- 5. 關鍵功能：自動寫入記帳本 (Auto-Journaling) ---
    
    # 判斷是賺錢還是賠錢
    if profit_loss > 0:
        # 賺錢 -> 記為「收入」
        new_record = models.Expense(
            amount=int(profit_loss),
            category="投資獲利",
            description=f"賣出 {stock.symbol} {sell_data.shares} 股 (獲利)",
            date=date.today(),
            record_type="income" # <--- 標記為收入
        )
        db.add(new_record)
        
    elif profit_loss <= 0:
        # 賠錢 -> 記為「支出」 (虧損視為一種支出)
        new_record = models.Expense(
            amount=int(abs(profit_loss)), # 轉為正數存入
            category="投資虧損",
            description=f"賣出 {stock.symbol} {sell_data.shares} 股 (停損)",
            date=date.today(),
            record_type="expense" # <--- 標記為支出
        )
        db.add(new_record)

    # 6. 全部存檔
    db.commit()

    return StockSellResponse(
        symbol=stock.symbol,
        sold_shares=sell_data.shares,
        realized_profit=round(profit_loss, 0)
    )