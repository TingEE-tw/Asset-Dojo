from fastapi import APIRouter
from APP.services import dashboard_service
from APP.schemas.dashboard import DashboardResponse

# 建立一個路由器
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/", response_model=DashboardResponse)
def get_dashboard():
    # 呼叫 Service 取得資料
    data = dashboard_service.get_dashboard_data()
    return data