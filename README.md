# 🥋 Asset Dojo 攻守道 (Asset Management System)

> **"記帳是防守，投資是進攻。"**
> 一個結合 **會計思維** 與 **投資策略** 的全端遊戲化理財系統。

## 📖 專案簡介 (Introduction)
Asset Dojo 是一個以 **淨值 (Net Worth)** 為核心視角的理財 App。解決傳統記帳軟體只能「節流」卻無法緩解通膨焦慮的痛點。透過 **成就系統 (Gamification)** 鼓勵使用者持續記錄，並結合股市損益追蹤，提供全方位的資產管理視角。

## 🚀 核心特色 (Features)

### 🛡️ 防守端：智慧記帳 (Defense)
* **雙向記帳**：支援「收入」與「支出」記錄，介面自動切換對應分類。
* **預算修練 (Budget Lock)**：
    * 設定每月支出目標（例如：$30,000）。
    * **誓約機制**：預算設定後鎖定 **3 個月** 不得更改，強制養成紀律。
* **悔棋機制**：支援刪除記帳紀錄，但僅限 **12 小時內** (超過時限即鎖定為歷史帳務)。

### ⚔️ 進攻端：股票管理 (Offense)
* **即時報價**：串接 `yfinance` API，即時監控持股現值。
* **智慧賣出**：優先賣出低成本庫存 (FIFO 邏輯)，自動計算已實現損益。
* **自動記帳**：賣出股票後，獲利/虧損自動回寫至記帳本，資產流動零時差。

### 🏆 遊戲化：成就道場 (Gamification)
* **階級修練**：從 **見習(Novice)** -> **黑帶** -> **師父** -> **宗師(Grandmaster)**。
* **動態解鎖**：
    * **階級依賴 (Prerequisite)**：需先完成上一級成就，才能挑戰下一級。
    * **月結算機制**：每月 1 日結算上月表現，判定是否達成「省錢」或「控管預算」成就。
* **視覺化獎章**：已解鎖成就顯示達成日期，未解鎖成就保持神秘或鎖定狀態。

### 📊 戰情室：高階儀表板 (Dashboard)
* **MoM 環比分析**：即時顯示本月支出與上月相比的增減幅度 (綠色/紅色燈號)。
* **收支透視**：甜甜圈圖分析支出類別，並列出 **Top 3 燒錢排行榜**。
* **歷年損益回顧**：YoY (Year-over-Year) 年度淨利與成長率分析 (近 3 年數據)。

## 🛠️ 技術棧 (Tech Stack)

* **Backend**: Python 3.13 + FastAPI
* **Database**: PostgreSQL 16 + SQLAlchemy (ORM)
* **Frontend**: Streamlit + Streamlit-Option-Menu
* **Data & Charts**: Pandas, Plotly, yfinance

---

## ⚙️ 環境需求 (Prerequisites)
在執行此專案之前，請確保您的電腦已安裝以下軟體：

1. **Python 3.10+**: [點此下載](https://www.python.org/downloads/) (安裝時請勾選 "Add Python to PATH")
2. **PostgreSQL 16**: [點此下載](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
    * 請記住您設定的 **密碼 (Password)**。
    * Port 請維持預設 **5432**。
3. **Git**: [點此下載](https://git-scm.com/downloads)

---

## ⚡ 快速啟動 (Quick Start)

### 1. 建立資料庫
1. 開啟 **pgAdmin 4**。
2. 對 `Databases` 按右鍵 -> `Create` -> `Database...`。
3. 名稱輸入：**`asset_dojo`**，按 Save 儲存。

### 2. 下載專案與安裝依賴
開啟終端機 (Terminal / CMD)，依序執行：

```bash
# 複製專案
git clone [https://github.com/您的帳號/Asset-Dojo.git](https://github.com/您的帳號/Asset-Dojo.git)
cd Asset-Dojo

# 建立虛擬環境 (建議)
python -m venv venv

# 啟動虛擬環境 (Windows)
.\venv\Scripts\activate
# 啟動虛擬環境 (Mac/Linux)
source venv/bin/activate

# 安裝所需套件
pip install -r requirements.txt

### 3. 設定環境變數 (.env)

在專案根目錄建立 .env 檔案，填入以下內容：

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

### 📅 第三部分：開發日誌與專案結構

```markdown
## 📅 開發日誌 (Dev Log)

### Phase 1: 基礎架構 (MVP) ✅
- [x] **環境建置**: Python 虛擬環境、FastAPI 安裝、Git 初始化。
- [x] **專案架構**: 確立 Clean Architecture (`APP/routers`, `APP/schemas`)。
- [x] **核心功能**: 實作基本的股票 CRUD (新增/賣出/即時報價)。

### Phase 2: 資料庫與防守端強化 ✅
- [x] **資料庫整合**: PostgreSQL + SQLAlchemy ORM。
- [x] **記帳模組 (Defense)**: 
    - 實作 **雙向記帳** (收入/支出) 與自動分類。
    - 支援 **12小時內刪除** 功能，防止誤刪歷史帳務。
- [x] **預算鎖定 (Budget)**:
    - 實作 **3個月誓約機制**，鎖定期間內無法修改預算目標。

### Phase 3: 遊戲化與高階儀表板 (Completed) ✅
- [x] **成就系統 (Gamification)**:
    - 建立 **Novice** 到 **Grandmaster** 四階層級。
    - 實作 **月結算邏輯**：每月 1 日自動判定上月表現。
    - 實作 **階級解鎖**：需完成前置成就才可挑戰下一級。
- [x] **UI/UX 升級**:
    - 導入 `streamlit-option-menu` 優化側邊導航。
    - **戰情室優化**: 加入 MoM 環比、Top 3 支出排行、YoY 年度損益回顧。

### Phase 4: 部署與雲端化 (Next Step) 🚧
- [ ] 設定 `requirements.txt` 與環境變數 (Production)。
- [ ] 部署後端至雲端平台 (Render / Railway)。
- [ ] 遷移資料庫至雲端 PostgreSQL。
- [ ] 讓應用程式可透過公開網址存取 (Mobile Friendly)。

---

## 📂 專案結構 (Project Structure)

```text
Asset Dojo/
├── APP/
│   ├── routers/
│   │   ├── stocks.py       # 股票交易邏輯
│   │   ├── expense.py      # 記帳與年度報表邏輯
│   │   ├── budget.py       # 預算鎖定邏輯
│   │   └── achievements.py # 成就結算系統
│   ├── models.py           # 資料庫模型 (ORM)
│   ├── schemas/            # Pydantic 資料驗證
│   ├── database.py         # DB 連線設定
│   └── main.py             # FastAPI 入口
├── Frontend/
│   └── app.py              # Streamlit 戰情室與介面
├── requirements.txt        # 專案依賴套件
└── README.md               # 說明文件