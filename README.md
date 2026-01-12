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