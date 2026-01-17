from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Boolean, Float
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

class Budget(Base):
    __tablename__ = "budget"

    id = Column(Integer, primary_key=True, index=True)
    monthly_limit = Column(Integer, nullable=False) # 每月預算上限
    updated_at = Column(DateTime, default=func.now()) # 上次設定的時間

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True) # 成就名稱 (ex: 🔰 起手式)
    description = Column(String)       # 描述 (ex: 第一次記帳)
    tier = Column(Integer)             # 等級 (1:見習, 2:黑帶, 3:師父, 4:宗師)
    icon = Column(String)              # 圖示 (ex: 🔰)
    
    # 判斷代碼 (用來讓程式知道這是哪個成就)
    code = Column(String, unique=True) # ex: "first_expense", "save_1000"
    
    # 狀態
    is_unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)