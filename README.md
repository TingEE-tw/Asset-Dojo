# 🥋 Asset Dojo (攻守道)

> **"記帳是防守，投資是進攻。"**
> 結合「生活記帳」與「台股投資」的遊戲化理財系統。

## 📖 專案簡介
Asset Dojo 是一個以 **淨值 (Net Worth)** 為核心視角的理財 App。解決傳統記帳軟體只能「節流」卻無法緩解通膨焦慮的痛點。透過成就系統 (Gamification) 鼓勵使用者持續記錄，並結合股市損益追蹤，提供全方位的資產管理視角。

## 🛠️ 技術棧 (Tech Stack)
* **Backend**: Python 3.13 + FastAPI
* **Database**: PostgreSQL 16
* **Frontend**: React (Next.js) + Tailwind CSS (規劃中)
* **DevOps**: GitHub Actions (規劃中)

---

## 📅 開發日誌 (Dev Log)

### Phase 1: 後端架構與環境建置 (2026/01/11)
- [x] **環境建置**: 
    - 建立 Python `venv` 虛擬環境。
    - 解決 Windows PowerShell 執行權限問題 (`Set-ExecutionPolicy`).
- [x] **框架安裝**: 完成 FastAPI 與 Uvicorn 安裝。
- [x] **架構重構**: 
    - 實作 Clean Architecture (`routers`, `services`, `schemas`)。
    - 解決 Python 模組引用路徑問題 (`APP` vs `app`)。
- [x] **API 開發**: 
    - 實作 `GET /dashboard` 測試接口 (Mock Data)。
- [x] **版本控制**: 
    - 完成 Git 初始化與 GitHub 倉庫連線。
    - 設定標準 `.gitignore` 排除虛擬環境。

### Phase 2: 資料庫與核心邏輯 (進行中)
- [ ] 安裝 PostgreSQL。
- [ ] 設定 `SQLAlchemy` ORM 連線。
- [ ] 設計 `User` 與 `Expense` 資料表模型。

---

## 🚀 如何啟動 (How to Run)

1. **啟動虛擬環境**:
   ```bash
   .\venv\Scripts\activate