from sqlalchemy import Column, Integer, String, Date, DateTime, Float # <--- 1. 這裡加了 Float
from sqlalchemy.sql import func
from APP.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    
    # 用來區分是 'expense' (支出) 還是 'income' (收入)
    record_type = Column(String, default="expense", nullable=False) 
    
    created_at = Column(DateTime, default=func.now())


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)    # 股票代號
    shares = Column(Integer, nullable=False)   # 持有股數
    average_cost = Column(Float, nullable=False) # 平均成本
    created_at = Column(DateTime, default=func.now())