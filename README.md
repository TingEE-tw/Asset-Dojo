# 🥋 Asset Dojo (攻守道)

> **"記帳是防守，投資是進攻。"**
> 結合「生活記帳」與「台股投資」的遊戲化理財系統。

## 📖 專案簡介
Asset Dojo 是一個以 **淨值 (Net Worth)** 為核心視角的理財 App。解決傳統記帳軟體只能「節流」卻無法緩解通膨焦慮的痛點。透過成就系統 (Gamification) 鼓勵使用者持續記錄，並結合股市損益追蹤，提供全方位的資產管理視角。

## 🛠️ 技術棧 (Tech Stack)
* **Backend**: Python 3.13 + FastAPI
* **Database**: PostgreSQL 16
* **Frontend**: Streamlit (Python Web UI)
* **Tools**: SQLAlchemy, Pydantic, yfinance, Plotly

---

## ⚙️ 環境需求與事前準備 (Prerequisites)
在執行此專案之前，請確保您的電腦已安裝以下軟體：

1.  **Python 3.10+**: [點此下載](https://www.python.org/downloads/)
    * *注意：安裝時請勾選 "Add Python to PATH"*
2.  **PostgreSQL 16**: [點此下載](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
    * 安裝時請記住您設定的 **密碼** (Password)。
    * Port 請維持預設 **5432**。
3.  **Git**: [點此下載](https://git-scm.com/downloads) (用於下載此專案)

---

## 🚀 快速啟動 (Quick Start)

### 1. 建立資料庫
1. 開啟 **pgAdmin 4** (安裝 PostgreSQL 時會附帶)。
2. 登入後，對 `Databases` 按右鍵 -> `Create` -> `Database...`。
3. 名稱輸入：**`asset_dojo`**。
4. 按 Save 儲存。

### 2. 下載專案與安裝依賴
開啟終端機 (Terminal / CMD)，依序執行：

```bash
# 複製專案
git clone [https://github.com/您的帳號/Asset-Dojo.git](https://github.com/您的帳號/Asset-Dojo.git)
cd Asset-Dojo

# 建立虛擬環境 (建議)
python -m venv venv

# 啟動虛擬環境
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安裝所需套件
pip install -r requirements.txt

```

### 3. 設定環境變數 (.env)

為了資訊安全，請在專案根目錄建立一個名為 `.env` 的檔案，並填入以下內容：

```env
DATABASE_URL=postgresql://postgres:您的密碼@localhost/asset_dojo

```

> ⚠️ 請將 `您的密碼` 換成您安裝 PostgreSQL 時設定的真實密碼。

### 4. 啟動系統

請開啟兩個終端機視窗分別執行：

**視窗 A (後端 Backend):**

```bash
uvicorn APP.main:app --reload

```

**視窗 B (前端 Frontend):**

```bash
streamlit run Frontend/app.py

```

系統啟動後，瀏覽器將自動開啟戰情室頁面！🎉

---

## 📅 開發日誌 (Dev Log)

### 2026/01 (專案啟動與核心功能)

> **本月目標**：完成前後端基礎架構、資料庫串接、以及記帳與股票核心功能。

* **Phase 1: 基礎架構**
* [x] **環境建置**: Python 虛擬環境、FastAPI 安裝、Git 版本控制初始化。
* [x] **專案架構**: 確立 Clean Architecture (`APP/routers`, `APP/schemas`)。


* **Phase 2: 資料庫與後端邏輯**
* [x] **資料庫整合**: 安裝 PostgreSQL，設定 SQLAlchemy ORM 連線。
* [x] **記帳模組**: 完成支出 (Expense) 的 CRUD API。
* [x] **股票模組**:
* 建立股票資料表 (`stocks`)。
* 整合 `yfinance` 抓取台股即時股價，自動計算市值與損益。




* **Phase 3: 前端視覺化與儀表板**
* [x] **Streamlit 介面**: 建立 Web 操作介面，取代 Swagger UI。
* [x] **戰情室 (Dashboard)**: 整合記帳與股票數據，即時計算淨值 (Net Worth)。
* [x] **圖表分析**: 導入 `Plotly` 繪製資產分佈圓餅圖與支出長條圖。
* [x] **資安強化**: 導入 `.env` 環境變數管理敏感資料。



```