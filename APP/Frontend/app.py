import streamlit as st
import requests
import pandas as pd
from datetime import date

# --- 設定 ---
# 這是我們後端的地址
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Asset Dojo 攻守道", page_icon="🥋", layout="wide")

st.title("🥋 Asset Dojo 攻守道")
st.caption("記帳是防守，投資是進攻")

# --- 側邊欄：功能選單 ---
menu = st.sidebar.selectbox("選擇功能", ["📊 資產總覽", "💰 記帳 (防守)", "📈 股票 (進攻)"])

# ==========================================
# 功能 1: 記帳 (防守)
# ==========================================
if menu == "💰 記帳 (防守)":
    st.header("📝 新增支出")
    
    # 1. 建立輸入表單
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("金額 ($)", min_value=1, step=10)
            category = st.selectbox("分類", ["食物", "交通", "娛樂", "居住", "其他"])
        with col2:
            date_input = st.date_input("日期", date.today())
            description = st.text_input("備註 (例如: 雞腿便當)")
            
        submit_btn = st.form_submit_button("新增支出")

    # 2. 按下按鈕後的邏輯
    if submit_btn:
        payload = {
            "amount": amount,
            "category": category,
            "description": description,
            "date": str(date_input)
        }
        try:
            # 呼叫我們自己寫的 FastAPI
            response = requests.post(f"{API_URL}/expenses/", json=payload)
            if response.status_code == 200:
                st.success("✅ 記帳成功！")
            else:
                st.error(f"❌ 失敗: {response.text}")
        except Exception as e:
            st.error(f"連線錯誤: {e}")

    st.divider()
    
    # 3. 顯示記帳列表
    st.header("📋 最近支出紀錄")
    try:
        response = requests.get(f"{API_URL}/expenses/")
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)

                # 1. 只挑選我們想看的欄位 (把 'id' 拿掉)
                # 並且重新排列順序：日期 -> 類別 -> 金額 -> 備註
                df = df[["date", "category", "amount", "description"]]

                # 2. 把欄位名稱改成中文 (更直觀)
                df.columns = ["日期", "類別", "金額", "備註"]

                # 3. 顯示表格
                # hide_index=True: 隱藏最左邊的 0,1,2 索引
                # use_container_width=True: 讓表格自動填滿寬度
                st.dataframe(
                    df, 
                    hide_index=True, 
                    use_container_width=True
                )
            else:
                st.info("目前還沒有任何記帳資料，快去新增一筆吧！")
    except Exception as e:
        st.error("⚠️ 無法連接到後端伺服器，請確認 uvicorn 是否有啟動。")

# ==========================================
# 功能 2: 股票 (進攻)
# ==========================================
elif menu == "📈 股票 (進攻)":
    st.header("📈 股票庫存管理")
    
    # 1. 新增股票表單
    with st.expander("➕ 新增持股 (買入)", expanded=True):
        with st.form("stock_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                symbol = st.text_input("股票代號", value="2330").upper()
            with col2:
                shares = st.number_input("股數 (Shares)", min_value=1, value=1000, step=100)
            with col3:
                price = st.number_input("買入價格 (Price)", min_value=0.1, value=500.0, step=0.5)
            
            submit_stock = st.form_submit_button("確認買入")

        if submit_stock:
            payload = {
                "symbol": symbol,
                "shares": shares,
                "price": price
            }
            try:
                res = requests.post(f"{API_URL}/stocks/", json=payload)
                if res.status_code == 200:
                    st.success(f"✅ 成功買入 {symbol} {shares} 股！")
                    st.rerun() # 重新整理頁面顯示最新資料
                else:
                    st.error(f"❌ 失敗: {res.text}")
            except Exception as e:
                st.error(f"連線錯誤: {e}")

    st.divider()

    # 2. 顯示庫存列表
    st.subheader("📦 目前持股清單")
    try:
        res = requests.get(f"{API_URL}/stocks/")
        if res.status_code == 200:
            stock_data = res.json()
            if stock_data:
                df_stock = pd.DataFrame(stock_data)
                
                # --- 這裡不需要再自己算成本了，後端都算好了 ---
                # 我們直接選要顯示的欄位
                df_stock = df_stock[[
                    "symbol", "shares", "average_cost", 
                    "current_price", "market_value", "profit"
                ]]
                
                # 改成中文標題
                df_stock.columns = [
                    "代號", "股數", "平均成本", 
                    "目前股價", "市值", "未實現損益"
                ]
                
                # 顯示表格
                st.dataframe(df_stock, hide_index=True, use_container_width=True)
                
                # --- 加碼功能：顯示總資產與總損益 ---
                total_value = df_stock["市值"].sum()
                total_profit = df_stock["未實現損益"].sum()
                
                # 用漂亮的指標卡顯示
                c1, c2 = st.columns(2)
                c1.metric("💰 股票總市值", f"${total_value:,.0f}")
                
                # 根據賺賠變色 (delta_color="normal" 會讓正數變綠/負數變紅)
                c2.metric("🚀 總損益", f"${total_profit:,.0f}", delta=f"{total_profit:,.0f}")
                
            else:
                st.info("目前沒有庫存，趕快進場吧！")
    except Exception as e:
        st.error("⚠️ 無法取得股票資料")


elif menu == "📊 資產總覽":
    st.info("🚧 儀表板開發中...")