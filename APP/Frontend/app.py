import streamlit as st
import requests
import pandas as pd
import plotly.express as px
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
    st.header("📋 收支紀錄明細")
    try:
        # 呼叫 GET API
        response = requests.get(f"{API_URL}/expenses/")
        if response.status_code == 200:
            data = response.json()
            if data:
                # 用 Pandas 把資料變漂亮
                df = pd.DataFrame(data)
                
                # --- 新增邏輯：防呆處理 ---
                # 如果資料庫裡有舊資料沒有 record_type，就預設填入 'expense'
                if "record_type" not in df.columns:
                    df["record_type"] = "expense"
                
                # --- 這裡我們調整要顯示的欄位 ---
                # 把 record_type (收入/支出) 加進來顯示
                df = df[["date", "record_type", "category", "amount", "description"]]
                
                # 把欄位名稱改成中文，讓閱讀更直觀
                df.columns = ["日期", "類型", "分類", "金額", "備註"]
                
                # 顯示表格
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("目前還沒有任何記帳資料，快去新增一筆吧！")
    except Exception as e:
        st.error("⚠️ 無法連接到後端伺服器，請確認 uvicorn 是否有啟動。")

# ==========================================
# 功能 2: 股票 (進攻)
# ==========================================
elif menu == "📈 股票 (進攻)":
    st.header("📈 股票庫存管理")
    
    # 這裡建立了兩個分頁：Tab1 買入、Tab2 賣出
    tab1, tab2 = st.tabs(["➕ 買入建倉", "➖ 賣出獲利"])

    # --- Tab 1: 買入功能 ---
    with tab1:
        st.subheader("💰 新增持股")
        with st.form("buy_stock_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                symbol = st.text_input("股票代號", value="2330").upper()
            with col2:
                shares = st.number_input("股數", min_value=1, value=1000, step=100)
            with col3:
                price = st.number_input("買入價格", min_value=0.1, value=500.0, step=0.5)
            
            submit_buy = st.form_submit_button("確認買入")

        if submit_buy:
            payload = {"symbol": symbol, "shares": shares, "price": price}
            try:
                res = requests.post(f"{API_URL}/stocks/", json=payload)
                if res.status_code == 200:
                    st.success(f"✅ 成功買入 {symbol} {shares} 股！")
                    st.rerun()
                else:
                    st.error(f"❌ 失敗: {res.text}")
            except Exception as e:
                st.error(f"連線錯誤: {e}")

    # --- Tab 2: 賣出功能 (這裡就是您消失的選單) ---
    with tab2:
        st.subheader("💸 獲利了結 / 停損")
        # 先去後端抓現在有哪些股票，才能讓使用者選
        try:
            res = requests.get(f"{API_URL}/stocks/")
            if res.status_code == 200 and res.json():
                my_stocks = res.json()
                
                # 製作下拉選單：格式為 "2330 (剩餘 1000 股)"
                stock_options = {f"{s['symbol']} (庫存: {s['shares']})": s['id'] for s in my_stocks}
                
                with st.form("sell_stock_form"):
                    # 下拉選單
                    selected_label = st.selectbox("選擇要賣出的股票", list(stock_options.keys()))
                    stock_id = stock_options[selected_label] # 拿到對應的 ID
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        sell_shares = st.number_input("賣出股數", min_value=1, step=100)
                    with c2:
                        sell_price = st.number_input("賣出價格", min_value=0.1, step=0.5)
                        
                    submit_sell = st.form_submit_button("確認賣出")

                if submit_sell:
                    payload = {"shares": sell_shares, "price": sell_price}
                    try:
                        # 呼叫 sell API
                        res = requests.post(f"{API_URL}/stocks/{stock_id}/sell", json=payload)
                        if res.status_code == 200:
                            result = res.json()
                            profit = result['realized_profit']
                            
                            # 根據賺賠顯示不同訊息
                            if profit > 0:
                                st.balloons() # 放氣球
                                st.success(f"🎉 恭喜！獲利了結，賺了 ${profit:,.0f} 元！(已自動記入收入)")
                            elif profit < 0:
                                st.error(f"💸 停損出場，虧損 ${abs(profit):,.0f} 元。(已自動記入支出)")
                            else:
                                st.info("⚖️ 打平出場。")
                                
                            import time
                            time.sleep(2) 
                            st.rerun()
                        else:
                            st.error(f"❌ 賣出失敗: {res.text}")
                    except Exception as e:
                        st.error(f"連線錯誤: {e}")
            else:
                st.info("目前沒有庫存可賣，請先去「買入」！")
        except Exception:
            st.warning("無法取得庫存列表")

    st.divider()

    # --- 下方顯示庫存列表 (維持不變) ---
    st.subheader("📦 目前持股清單")
    try:
        res = requests.get(f"{API_URL}/stocks/")
        if res.status_code == 200:
            stock_data = res.json()
            if stock_data:
                df_stock = pd.DataFrame(stock_data)
                df_stock = df_stock[[
                    "symbol", "shares", "average_cost", 
                    "current_price", "market_value", "profit"
                ]]
                df_stock.columns = ["代號", "股數", "平均成本", "目前股價", "市值", "未實現損益"]
                st.dataframe(df_stock, hide_index=True, use_container_width=True)
                
                total_value = df_stock["市值"].sum()
                total_profit = df_stock["未實現損益"].sum()
                
                c1, c2 = st.columns(2)
                c1.metric("💰 股票總市值", f"${total_value:,.0f}")
                c2.metric("🚀 帳面損益", f"${total_profit:,.0f}", delta=f"{total_profit:,.0f}")
            else:
                st.info("目前沒有庫存，趕快進場吧！")
    except Exception as e:
        st.error("⚠️ 無法取得股票資料")


elif menu == "📊 資產總覽":
    st.header("🏆 資產戰情室 (Dashboard)")
    
    # --- 1. 撈取資料 (同時抓股票和記帳) ---
    total_assets = 0   # 股票總值
    total_expense = 0  # 總支出
    total_income = 0   # 總收入 (新增這個變數)
    net_worth = 0      # 總淨值
    
    stock_df = None
    expense_df = None

    col1, col2, col3 = st.columns(3)

    try:
        # A. 抓股票資產
        res_stock = requests.get(f"{API_URL}/stocks/")
        if res_stock.status_code == 200:
            stock_data = res_stock.json()
            if stock_data:
                stock_df = pd.DataFrame(stock_data)
                total_assets = stock_df["market_value"].sum()

        # B. 抓記帳資料 (這裡邏輯變複雜了，因為要分開算收入和支出)
        res_expense = requests.get(f"{API_URL}/expenses/")
        if res_expense.status_code == 200:
            expense_data = res_expense.json()
            if expense_data:
                expense_df = pd.DataFrame(expense_data)
                
                # 防呆：如果沒有 record_type 欄位，先預設都是支出
                if "record_type" not in expense_df.columns:
                    expense_df["record_type"] = "expense"
                
                # 1. 篩選出「支出 (expense)」並加總
                expenses_only = expense_df[expense_df["record_type"] == "expense"]
                total_expense = expenses_only["amount"].sum()
                
                # 2. 篩選出「收入 (income)」並加總
                income_only = expense_df[expense_df["record_type"] == "income"]
                total_income = income_only["amount"].sum()

        # C. 計算淨值 (新公式)
        # 邏輯：你的身價 = 股票現值 + 手上的現金
        # 手上的現金 = 總收入 - 總支出
        cash_on_hand = total_income - total_expense
        net_worth = total_assets + cash_on_hand

        # --- 2. 顯示三大指標卡 ---
        with col1:
            st.metric("💰 股票總資產", f"${total_assets:,.0f}")
        with col2:
            # 這裡改顯示「現金結餘」，如果收入大於支出就是綠色，反之紅色
            st.metric("💵 現金結餘 (收入-支出)", f"${cash_on_hand:,.0f}", delta=f"{cash_on_hand:,.0f}")
        with col3:
            st.metric("💎 總淨值 (Net Worth)", f"${net_worth:,.0f}")

        st.divider()

        # --- 3. 視覺化圖表區 ---
        chart1, chart2 = st.columns(2)

        # 左邊：資產配置圓餅圖 (維持不變)
        with chart1:
            st.subheader("🍰 股票資產分佈")
            if stock_df is not None and not stock_df.empty:
                fig = px.pie(stock_df, values='market_value', names='symbol', title='持股佔比 (依市值)', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("尚無股票資產")

        # 右邊：支出分類長條圖 (只統計支出類型)
        with chart2:
            st.subheader("📊 支出分類統計")
            if expense_df is not None and not expense_df.empty:
                # 這裡要小心，只畫「支出」的圖，不要把「收入」也畫進去
                expenses_only_df = expense_df[expense_df["record_type"] == "expense"]
                
                if not expenses_only_df.empty:
                    category_sum = expenses_only_df.groupby("category")["amount"].sum().reset_index()
                    fig2 = px.bar(category_sum, x='category', y='amount', title='各類別消費總額', color='category')
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("尚無支出紀錄")
            else:
                st.info("尚無收支紀錄")

    except Exception as e:
        st.error(f"系統連線錯誤: {e}")