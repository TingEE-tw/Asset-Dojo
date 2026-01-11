from APP.schemas.dashboard import DashboardResponse, BudgetInfo, StockSummary

def get_dashboard_data() -> DashboardResponse:
    """
    模擬從資料庫撈取並計算後的數據
    """
    # 模擬邏輯：之後這裡會變成 db.query(...)
    budget_data = BudgetInfo(
        total=30000, 
        spent=12500, 
        remaining=30000-12500
    )
    
    stock_data = StockSummary(
        total_value=540000,
        profit=23000,
        profit_percent=4.4
    )

    return DashboardResponse(
        budget=budget_data,
        daily_trend=[100, 200, 50, 300, 0, 150, 600], # 模擬七天花費
        stock=stock_data
    )