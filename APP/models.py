from sqlalchemy import Column, Integer, String, Date, DateTime, Float # <--- 1. 這裡加了 Float
from sqlalchemy.sql import func
from APP.database import Base

# --- 原本的記帳模型 ---
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())

# --- 2. 新增這個股票模型 ---
class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)    # 股票代號
    shares = Column(Integer, nullable=False)   # 持有股數
    average_cost = Column(Float, nullable=False) # 平均成本
    created_at = Column(DateTime, default=func.now())