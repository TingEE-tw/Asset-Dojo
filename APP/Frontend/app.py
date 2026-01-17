import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import date
from streamlit_option_menu import option_menu

# --- 設定 ---
# 這是我們後端的地址
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Asset Dojo 攻守道", page_icon="🥋", layout="wide")

st.title("🥋 Asset Dojo 攻守道")
st.caption("記帳是防守，投資是進攻")

# --- 側邊欄：功能選單 ---
with st.sidebar:
    st.title("🥋 Asset Dojo")
    
    # 使用 option_menu 取代原本的 radio
    # 這裡的 icons 使用的是 Bootstrap Icons (https://icons.getbootstrap.com/)
    menu = option_menu(
        menu_title="",    # 選單標題 (可以留空 None)
        options=["資產總覽", "記帳 (防守)", "股票 (進攻)", "成就道場"], # 選項名稱
        icons=["speedometer2", "shield-fill", "graph-up-arrow", "trophy-fill"], # 對應的圖示
        menu_icon="cast",        # 選單左上角的小圖示
        default_index=0,         # 預設選中第幾個
        styles={
            "container": {"padding": "5px", "background-color": "#262730"},
            "icon": {"color": "orange", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#444"},
            "nav-link-selected": {"background-color": "#FF4B4B"},
        }
    )
    
    st.divider()

    # --- 預算設定區塊 (維持原本邏輯，只稍微調整位置) ---
    st.subheader("⚙️ 修煉")

# 1. 抓取目前預算狀態
try:
    res_budget = requests.get(f"{API_URL}/budget/")
    if res_budget.status_code == 200:
        b_data = res_budget.json()
        current_budget = b_data['amount']
        can_update = b_data['can_update']
        next_date = b_data['next_update_date']
        
        # 顯示目前目標
        st.sidebar.metric("每月支出目標", f"${current_budget:,.0f}")
        
        # 2. 修改預算 (使用 expander 收納，保持介面整潔)
        with st.sidebar.expander("更改目標設定"):
            if can_update:
                new_budget = st.number_input("設定新目標", min_value=1000, step=1000, value=current_budget if current_budget > 0 else 30000)
                if st.button("🔒 立下誓約 (鎖定3個月)"):
                    try:
                        res_set = requests.post(f"{API_URL}/budget/", json={"amount": new_budget})
                        if res_set.status_code == 200:
                            st.sidebar.success("✅ 設定成功！修煉開始！")
                            st.rerun()
                        else:
                            st.sidebar.error(res_set.json()['detail'])
                    except Exception as e:
                        st.sidebar.error(f"連線錯誤: {e}")
            else:
                # 鎖定狀態：顯示倒數計時
                # 把 ISO 時間字串轉得好看一點
                unlock_day = next_date.split("T")[0]
                st.info(f"🔒 目標鎖定中\n\n下次可調整日期：\n{unlock_day}")
                st.caption("「朝令夕改，乃兵家大忌。」")

except Exception:
    st.sidebar.warning("無法讀取預算設定")

if menu == "資產總覽":
    st.header("🏆 資產戰情室 (Dashboard)")
    st.caption("運籌帷幄之中，決勝千里之外。")

    # --- 1. 撈取資料 ---
    try:
        # 取得所有記帳資料
        res_exp = requests.get(f"{API_URL}/expenses/")
        # 取得股票現值 (為了算淨值)
        res_stock = requests.get(f"{API_URL}/stocks/")
        
        if res_exp.status_code == 200 and res_stock.status_code == 200:
            data_exp = res_exp.json()
            data_stock = res_stock.json()
            
            # 轉換為 DataFrame 方便計算
            df = pd.DataFrame(data_exp)
            
            # --- 資料預處理 ---
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                df["month"] = df["date"].dt.strftime("%Y-%m") # 建立月份欄位
                # 確保有 record_type，沒有的補 expense
                if "record_type" not in df.columns:
                    df["record_type"] = "expense"
            else:
                # 建立空的 DataFrame 防止報錯
                df = pd.DataFrame(columns=["date", "amount", "category", "record_type", "month"])

            # --- 2. 計算關鍵指標 (KPIs) ---
            
            # A. 股票總市值
            stock_value = 0
            if data_stock:
                stock_value = sum(s['market_value'] for s in data_stock)

            # B. 現金結餘 (總收入 - 總支出)
            total_income = df[df["record_type"] == "income"]["amount"].sum()
            total_expense = df[df["record_type"] == "expense"]["amount"].sum()
            cash_balance = total_income - total_expense
            
            # C. 總淨值
            net_worth = cash_balance + stock_value

            # D. [新功能] 環比分析 (MoM) - 與上個月比較
            # 取得本月與上個月的月份字串
            today = date.today()
            this_month_str = today.strftime("%Y-%m")
            last_month_date = today - pd.DateOffset(months=1)
            last_month_str = last_month_date.strftime("%Y-%m")

            # 計算本月支出
            mask_this_month = (df["month"] == this_month_str) & (df["record_type"] == "expense")
            exp_this_month = df[mask_this_month]["amount"].sum()

            # 計算上月支出
            mask_last_month = (df["month"] == last_month_str) & (df["record_type"] == "expense")
            exp_last_month = df[mask_last_month]["amount"].sum()

            # 計算變化率 (避免除以 0)
            if exp_last_month > 0:
                delta_percent = ((exp_this_month - exp_last_month) / exp_last_month) * 100
            else:
                delta_percent = 0 # 無上月資料

            # --- 3. 顯示頂部 KPI 卡片 ---
            col1, col2, col3 = st.columns(3)
            col1.metric("💎 總淨值 (Net Worth)", f"${net_worth:,.0f}")
            col2.metric("💵 現金結餘", f"${cash_balance:,.0f}")
            
            # 這裡的 delta 我們用「支出變化」
            # 如果支出變多 (正數)，顯示紅色 (inverse)；支出變少 (負數)，顯示綠色
            col3.metric(
                "📅 本月支出", 
                f"${exp_this_month:,.0f}", 
                delta=f"{delta_percent:+.1f}% (較上月)", 
                delta_color="inverse" # 讓支出增加變紅色，減少變綠色
            )
            
            st.divider()

            # --- 4. 中段：支出分析 (圖表 + Top 3) ---
            st.subheader("📊 支出透視")
            
            if not df.empty:
                c1, c2 = st.columns([2, 1]) # 左邊寬一點放圖，右邊放排行榜

                with c1:
                    # [圖表] 本月支出類別佔比 (Donut Chart)
                    # 只篩選「支出」且「本月」(如果本月沒資料，就顯示全部時間的，避免空白)
                    target_df = df[mask_this_month]
                    chart_title = "本月支出分佈"
                    if target_df.empty:
                        target_df = df[df["record_type"] == "expense"] # fallback 到全部
                        chart_title = "歷史總支出分佈 (本月尚無資料)"

                    if not target_df.empty:
                        fig_pie = px.pie(
                            target_df, 
                            values="amount", 
                            names="category", 
                            title=chart_title,
                            hole=0.4, # 甜甜圈
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    else:
                        st.info("尚無支出紀錄")

                with c2:
                    # [列表] Top 3 支出排行榜
                    st.write("🔥 **本月燒錢排行榜 (Top 3)**")
                    
                    if not target_df.empty:
                        # 分組加總 -> 排序 -> 取前三
                        top3 = target_df.groupby("category")["amount"].sum().sort_values(ascending=False).head(3)
                        
                        for i, (cat, amt) in enumerate(top3.items()):
                            rank_icon = ["🥇", "🥈", "🥉"][i]
                            st.write(f"### {rank_icon} {cat}")
                            st.write(f"**${amt:,.0f}**")
                            # 顯示佔總支出的比例
                            total_target = target_df["amount"].sum()
                            pct = (amt / total_target) * 100
                            st.progress(pct / 100, text=f"佔比 {pct:.1f}%")
                    else:
                        st.caption("恭喜！本月還沒有亂花錢。")

            st.divider()

            # --- 5. 底部：收支趨勢與結餘 (Bar Chart) ---
            st.subheader("📅 收支趨勢 (累計節省)")
            
            if not df.empty:
                # 依月份分組，計算收入與支出
                monthly_stats = df.groupby(["month", "record_type"])["amount"].sum().reset_index()
                
                # 使用 Grouped Bar Chart
                fig_bar = px.bar(
                    monthly_stats, 
                    x="month", 
                    y="amount", 
                    color="record_type", 
                    barmode="group", # 並排顯示
                    title="每月收入 vs 支出對比",
                    labels={"amount": "金額", "month": "月份", "record_type": "類型"},
                    color_discrete_map={"income": "#2ecc71", "expense": "#e74c3c"} # 綠收紅支
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # 計算每個月實際存了多少 (Income - Expense)
                # 這裡做一個 pivot table 比較好算
                pivot_df = df.pivot_table(index="month", columns="record_type", values="amount", aggfunc="sum", fill_value=0)
                if "income" in pivot_df.columns and "expense" in pivot_df.columns:
                    pivot_df["saved"] = pivot_df["income"] - pivot_df["expense"]
                    
                    # 顯示最近幾個月的結餘文字
                    with st.expander("查看每月詳細結餘 (Net Cash Flow)"):
                        st.dataframe(pivot_df.sort_index(ascending=False), use_container_width=True)

            st.divider()

            # --- 6. [新功能] 歷年損益回顧 (YoY Analysis) ---
            st.subheader("📆 歷年戰績回顧 (近3年)")
            
            try:
                res_annual = requests.get(f"{API_URL}/expenses/annual_summary")
                if res_annual.status_code == 200:
                    annual_data = res_annual.json()
                    
                    if annual_data:
                        # 我們用 columns 來顯示每年的卡片
                        cols = st.columns(len(annual_data))
                        
                        for idx, item in enumerate(annual_data):
                            year = item['year']
                            profit = item['net_profit']
                            growth = item['growth_pct']
                            
                            with cols[idx]:
                                # 根據獲利正負顯示顏色
                                border_color = "green" if profit >= 0 else "red"
                                with st.container(border=True):
                                    st.markdown(f"### {year} 年")
                                    
                                    # 顯示淨利
                                    st.metric(
                                        label="年度淨利 (Net Profit)",
                                        value=f"${profit:,.0f}",
                                        # 顯示成長率 (如果是 None 就不顯示 delta)
                                        delta=f"{growth:+.1f}% (YoY)" if growth is not None else None,
                                        delta_color="normal" # 正成長綠色，負成長紅色
                                    )
                                    
                                    # 顯示收支細節小字
                                    st.caption(f"💰 總收入: ${item['total_income']:,.0f}")
                                    st.caption(f"💸 總支出: ${item['total_expense']:,.0f}")
                    else:
                        st.info("尚無跨年度的資料可供分析")
            except Exception as e:
                st.error(f"無法讀取年度分析: {e}")
                
    except Exception as e:
        st.error(f"資料讀取錯誤: {e}")
        
# ==========================================
# 功能 : 記帳 (防守)
# ==========================================
elif menu == "記帳 (防守)":
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
                    # --- 修改這裡：顯示後端回傳的真實錯誤原因 ---
                    try:
                        # 嘗試抓取後端的 detail 訊息
                        error_msg = res.json().get("detail", "刪除失敗")
                    except:
                        error_msg = res.text
                    
                    st.error(f"❌ {error_msg}") # 這樣就會顯示「此紀錄已超過 12 小時...」
                    
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
# 功能 : 股票 (進攻)
# ==========================================
elif menu == "股票 (進攻)":
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

elif menu == "成就道場":
    st.header("🏆 成就道場 (Hall of Fame)")
    
    # 顯示目前年月，提醒使用者這是月結算機制
    current_period = date.today().strftime("%Y年%m月")
    st.caption(f"📅 目前週期：{current_period} (當月成就將於次月 1 日結算)")
    
    try:
        res = requests.get(f"{API_URL}/achievements/")
        if res.status_code == 200:
            ach_list = res.json()
            
            # 計算總進度
            unlocked_count = sum(1 for a in ach_list if a['is_unlocked'])
            total_count = len(ach_list)
            st.progress(unlocked_count / total_count, text=f"總修煉進度：{unlocked_count}/{total_count}")
            st.divider()

            # [前端邏輯優化] 建立一個「可見清單」
            # 我們需要知道每個成就的「前置條件」是誰，這需要在前端也簡單定義一下關係，
            # 或是利用後端的 tier 邏輯。這裡用一個更聰明的方法：
            # 邏輯：對於每一個成就，如果它是 Level 1 -> 顯示
            #       如果它的 Level > 1 -> 只有在「上一級已解鎖」時才顯示
            
            # 為了方便，我們把後端的 PREREQUISITES 邏輯簡單複製一份到前端做顯示過濾
            # (這比再寫一支 API 簡單)
            FRONTEND_PREREQ = {
                "save_300": "save_1",
                "save_1000": "save_300",
                "save_5000": "save_1000",
                "save_10000": "save_5000",
                "success_streak_3": "first_success",
                "success_streak_6": "success_streak_3",
                "fail_streak_3": "first_fail",
                "fail_streak_6": "fail_streak_3",
                "super_save": "success_streak_3"
            }
            
            # 建立一個 {code: is_unlocked} 的快速查表
            status_map = {a['code']: a['is_unlocked'] for a in ach_list}
            
            visible_achs = []
            for ach in ach_list:
                code = ach['code']
                is_unlocked = ach['is_unlocked']
                
                # 規則 1: 已經解鎖的，當然要顯示
                if is_unlocked:
                    visible_achs.append(ach)
                    continue
                
                # 規則 2: 還沒解鎖，但它是 Level 1 (新手任務)，也要顯示
                if ach['tier'] == 1:
                    visible_achs.append(ach)
                    continue
                    
                # 規則 3: 還沒解鎖，是高階任務，檢查上一級解鎖沒
                parent_code = FRONTEND_PREREQ.get(code)
                if parent_code and status_map.get(parent_code, False):
                    # 如果爸爸解鎖了，兒子就可以出來見人了 (作為下一個挑戰)
                    visible_achs.append(ach)

            # --- 開始繪製 (只繪製 visible_achs) ---
            # 為了保持版面整齊，我們還是依照 Tier 分類顯示
            tiers = {
                1: "🔰 Level 1: 見習 (Novice)",
                2: "🥋 Level 2: 黑帶 (Black Belt)",
                3: "🧘 Level 3: 師父 (Master)",
                4: "👑 Level 4: 宗師 (Grandmaster)"
            }

            for t_id, t_name in tiers.items():
                # 篩選屬於這個層級且「可見」的成就
                tier_items = [a for a in visible_achs if a['tier'] == t_id]
                
                if not tier_items:
                    continue # 如果這個等級沒有可見的成就，就整區隱藏
                
                st.subheader(t_name)
                cols = st.columns(3)
                for idx, ach in enumerate(tier_items):
                    with cols[idx % 3]:
                        container = st.container(border=True)
                        if ach['is_unlocked']:
                            # 解鎖樣式
                            container.markdown(f"### {ach['icon']} {ach['name']}")
                            container.caption(f"✅ {ach['description']}")
                            if ach['unlocked_at']:
                                # [修改] 顯示達成年月 (YYYY-MM)
                                dt_obj = date.fromisoformat(ach['unlocked_at'].split("T")[0])
                                date_str = dt_obj.strftime("%Y年%m月")
                                container.text(f"達成於: {date_str}")
                        else:
                            # 鎖定樣式 (下一個挑戰)
                            container.markdown(f"### 🔒 {ach['name']}")
                            container.caption(f"{ach['description']}") 
                            container.info("修煉中...")
                
                st.divider()

    except Exception as e:
        st.error(f"無法讀取成就資料: {e}")