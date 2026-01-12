from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------------------------------------------------
# 1. 設定資料庫連線網址
# 格式: postgresql://帳號:密碼@網址:Port/資料庫名稱
# ⚠️ 請將 'password' 換成您剛剛設定的真實密碼！
# ---------------------------------------------------
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:sake0829@localhost/asset_dojo"

# 2. 建立資料庫引擎 (Engine)
# 這是 SQLAlchemy 用來與資料庫對話的核心物件
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# 3. 建立 Session 工廠 (SessionLocal)
# 每次請求進來時，我們會用這個工廠產生一個新的 Session (連線)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 宣告 Base 模型
# 以後我們所有的資料表模型 (User, Expense...) 都要繼承這個 Base
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()