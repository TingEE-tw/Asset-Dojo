import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import yfinance as yf
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
    st.header("💰 記帳 (防守)")

    # 定義分類清單 (讓選單變聰明)
    EXPENSE_CATS = ["飲食", "交通", "娛樂", "居住", "教育", "醫療", "投資虧損", "其他"]
    INCOME_CATS = ["薪資", "獎金", "投資獲利", "股利", "兼職", "零用錢", "其他"]

    # 1. 使用分頁切換：支出 vs 收入
    tab1, tab2 = st.tabs(["💸 新增支出", "💰 新增收入"])

    # --- Tab 1: 支出 (Expense) ---
    with tab1:
        with st.form("expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                # 預設選單帶入「支出分類」
                cat_exp = st.selectbox("支出分類", EXPENSE_CATS)
                date_exp = st.date_input("日期", date.today(), key="date_exp")
            with col2:
                amount_exp = st.number_input("金額", min_value=1, step=10, key="amt_exp")
                desc_exp = st.text_input("備註 (選填)", key="desc_exp")
            
            submit_exp = st.form_submit_button("確認支出 (記一筆)")

        if submit_exp:
            payload = {
                "amount": amount_exp,
                "category": cat_exp,
                "description": desc_exp,
                "date": str(date_exp),
                "record_type": "expense"  # <--- 關鍵：標記為支出
            }
            try:
                res = requests.post(f"{API_URL}/expenses/", json=payload)
                if res.status_code == 200:
                    st.success("✅ 支出紀錄成功！")
                    st.rerun()
                else:
                    st.error(f"❌ 失敗: {res.text}")
            except Exception as e:
                st.error(f"連線錯誤: {e}")

    # --- Tab 2: 收入 (Income) ---
    with tab2:
        with st.form("income_form"):
            col1, col2 = st.columns(2)
            with col1:
                # 預設選單帶入「收入分類」
                cat_inc = st.selectbox("收入分類", INCOME_CATS)
                date_inc = st.date_input("日期", date.today(), key="date_inc")
            with col2:
                amount_inc = st.number_input("金額", min_value=1, step=10, key="amt_inc")
                desc_inc = st.text_input("備註 (選填)", key="desc_inc")
            
            submit_inc = st.form_submit_button("確認收入 (進帳了)")

        if submit_inc:
            payload = {
                "amount": amount_inc,
                "category": cat_inc,
                "description": desc_inc,
                "date": str(date_inc),
                "record_type": "income"  # <--- 關鍵：標記為收入
            }
            try:
                res = requests.post(f"{API_URL}/expenses/", json=payload)
                if res.status_code == 200:
                    st.balloons()  # 賺錢值得慶祝！
                    st.success("🎉 收入紀錄成功！")
                    st.rerun()
                else:
                    st.error(f"❌ 失敗: {res.text}")
            except Exception as e:
                st.error(f"連線錯誤: {e}")

    st.divider()

    # 2. 顯示收支列表 (含刪除功能)
    st.subheader("📋 收支紀錄明細")
    
    # 這裡加入一個「刪除區塊」
    with st.expander("🗑️ 刪除紀錄 (點擊展開)"):
        del_id = st.number_input("輸入要刪除的 ID", min_value=1, step=1)
        if st.button("確認刪除"):
            try:
                res = requests.delete(f"{API_URL}/expenses/{del_id}")
                if res.status_code == 204:
                    st.success(f"✅ ID {del_id} 已刪除")
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 刪除失敗 (可能 ID 不存在)")
            except Exception as e:
                st.error(f"連線錯誤: {e}")

    # 列表顯示邏輯
    try:
        response = requests.get(f"{API_URL}/expenses/")
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                
                if "record_type" not in df.columns:
                    df["record_type"] = "expense"
                
                # 為了讓使用者知道 ID (以便刪除)，我們把 ID 欄位加回來
                df = df[["id", "date", "record_type", "category", "amount", "description"]]
                df.columns = ["ID", "日期", "類型", "分類", "金額", "備註"]
                
                # 依照日期降序排列 (新的在上面)
                df = df.sort_values(by="日期", ascending=False)
                
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("目前還沒有任何記帳資料，快去新增一筆吧！")
    except Exception as e:
        st.error("⚠️ 無法連接到後端伺服器")

# ==========================================
# 功能 2: 股票 (進攻)
# ==========================================
elif menu == "📈 股票 (進攻)":
    st.header("📈 股票庫存管理")
    
    tab1, tab2 = st.tabs(["➕ 買入建倉", "➖ 賣出獲利"])

    # --- Tab 1: 買入功能 ---
    with tab1:
        st.subheader("💰 新增持股")
        
        # [UX 優化] 1. 將輸入代號移到表單外，以便即時抓取股價
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            symbol_input = st.text_input("輸入股票代號 (例如 2330)", value="2330").upper()
        with col_input2:
            # [UX 優化] 2. 選擇單位 (張 vs 股)
            unit_type = st.radio("選擇單位", ["張 (1000股)", "股 (零股)"], horizontal=True)

        # [UX 優化] 3. 自動抓取當前股價 (作為預設值)
        current_price_guess = 0.0
        try:
            if symbol_input:
                # 這裡直接用 yfinance 抓即時股價給前端看
                ticker = yf.Ticker(f"{symbol_input}.TW")
                # 嘗試抓取最後收盤價 (快速查詢)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current_price_guess = float(hist["Close"].iloc[-1])
                    st.caption(f"🔎 {symbol_input} 參考市價: {current_price_guess}")
        except Exception:
            pass # 抓不到就算了，不影響主流程

        # --- 買入表單 ---
        with st.form("buy_stock_form"):
            col1, col2 = st.columns(2)
            with col1:
                # 根據單位顯示不同的說明
                if "張" in unit_type:
                    buy_qty = st.number_input("買入數量 (張)", min_value=1, value=1, step=1)
                else:
                    buy_qty = st.number_input("買入數量 (股)", min_value=1, value=1000, step=100)
            
            with col2:
                # 預設值帶入剛剛抓到的股價
                price = st.number_input("買入價格 (單股)", min_value=0.1, value=current_price_guess if current_price_guess > 0 else 500.0, step=0.5)
            
            submit_buy = st.form_submit_button("確認買入")

        if submit_buy:
            # [邏輯轉換] 如果選的是「張」，要乘以 1000
            final_shares = buy_qty * 1000 if "張" in unit_type else buy_qty
            
            payload = {"symbol": symbol_input, "shares": int(final_shares), "price": price}
            try:
                res = requests.post(f"{API_URL}/stocks/", json=payload)
                if res.status_code == 200:
                    st.success(f"✅ 成功買入 {symbol_input} {final_shares} 股！")
                    st.rerun()
                else:
                    st.error(f"❌ 失敗: {res.text}")
            except Exception as e:
                st.error(f"連線錯誤: {e}")

# --- Tab 2: 賣出功能 (智慧版) ---
    with tab2:
        st.subheader("💸 獲利了結 / 停損")
        
        # 1. 輸入代號與單位
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            # 這裡加了 .strip() 去除前後空白，防止使用者不小心多打空格
            sell_symbol = st.text_input("賣出代號", value="2330", key="sell_symbol").strip().upper()
        with col_s2:
            sell_unit_type = st.radio("賣出單位", ["張", "股"], horizontal=True, key="sell_unit_smart")

        # 2. 自動查詢：先查庫存 -> 沒庫存則查 Yahoo Finance -> 真的都沒有才給預設值
        total_shares_owned = 0
        current_market_price = 0.0 # 初始化

        try:
            # A. 嘗試從後端 API 抓庫存資料
            res = requests.get(f"{API_URL}/stocks/")
            if res.status_code == 200:
                all_stocks = res.json()
                target_batches = [s for s in all_stocks if s['symbol'] == sell_symbol]
                
                if target_batches:
                    # 情況 1: 有庫存 -> 用庫存裡的最新價格
                    total_shares_owned = sum(s['shares'] for s in target_batches)
                    current_market_price = target_batches[0].get('current_price', 0)
                    st.info(f"📦 {sell_symbol} 總庫存: {total_shares_owned} 股")
                else:
                    # 情況 2: 沒庫存 -> 嘗試去 Yahoo Finance 抓即時股價
                    st.warning(f"⚠️ 查無 {sell_symbol} 的庫存，將嘗試抓取即時市價...")
                    try:
                        ticker = yf.Ticker(f"{sell_symbol}.TW")
                        hist = ticker.history(period="1d")
                        if not hist.empty:
                            current_market_price = float(hist["Close"].iloc[-1])
                            st.caption(f"🔎 Yahoo Finance 報價: {current_market_price}")
                    except:
                        pass # 抓不到就算了
        except:
            pass

        # 3. 賣出表單
        with st.form("smart_sell_form"):
            c1, c2 = st.columns(2)
            with c1:
                if sell_unit_type == "張":
                    sell_qty = st.number_input("賣出數量 (張)", min_value=1, step=1, key="s_qty_1")
                else:
                    sell_qty = st.number_input("賣出數量 (股)", min_value=1, step=100, key="s_qty_2")
            with c2:
                # 這裡做最後的防呆：如果上面努力了半天還是 0 (例如斷網或代號打錯)，就給 10.0 防止報錯
                final_default_price = float(current_market_price) if current_market_price > 0 else 10.0
                
                sell_price = st.number_input(
                    "賣出價格 (單股)", 
                    min_value=0.1, 
                    value=final_default_price, 
                    step=0.5
                )
            
            submit_smart_sell = st.form_submit_button("確認賣出")

        # ... (下方的 submit 邏輯不用動)

        if submit_smart_sell:
            # 換算股數
            final_sell_shares = sell_qty * 1000 if sell_unit_type == "張" else sell_qty
            
            # 防呆：不能賣超過總庫存
            if final_sell_shares > total_shares_owned:
                st.error(f"❌ 庫存不足！您只有 {total_shares_owned} 股，卻想賣 {final_sell_shares} 股。")
            else:
                # 呼叫新的智慧 API
                payload = {
                    "symbol": sell_symbol,
                    "shares": int(final_sell_shares),
                    "price": sell_price
                }
                try:
                    res = requests.post(f"{API_URL}/stocks/sell/smart", json=payload)
                    if res.status_code == 200:
                        result = res.json()
                        profit = result['realized_profit']
                        
                        if profit > 0:
                            st.balloons()
                            st.success(f"🎉 成功賣出！系統已優先賣出低價庫存，獲利 ${profit:,.0f}")
                        elif profit < 0:
                            st.error(f"💸 停損賣出，虧損 ${abs(profit):,.0f}")
                        else:
                            st.info("⚖️ 打平出場。")
                        
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ 賣出失敗: {res.text}")
                except Exception as e:
                    st.error(f"連線錯誤: {e}")

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