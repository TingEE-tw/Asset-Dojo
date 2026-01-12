import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. 載入 .env 檔案裡的設定
load_dotenv()

# 2. 從環境變數讀取連線字串 (不再寫死密碼)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 3. 建立資料庫引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. 建立 Session 工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. 宣告 Base 模型
Base = declarative_base()

# 6. 資料庫依賴 (這個函式一定要留著，不然 API 會壞掉！)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()