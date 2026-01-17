from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date
from APP.database import get_db
from APP import models
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/achievements", tags=["achievements"])

# --- 定義傳輸格式 ---
class AchievementSchema(BaseModel):
    name: str
    description: str
    tier: int
    icon: str
    is_unlocked: bool
    unlocked_at: Optional[datetime]
    code: str  # 前端篩選需要用到 code

    class Config:
        from_attributes = True

# --- 定義成就清單 (Master List) ---
INITIAL_ACHIEVEMENTS = [
    # Level 1
    {"code": "first_expense", "tier": 1, "icon": "🔰", "name": "起手式", "desc": "完成第 1 筆記帳"},
    {"code": "first_fail",    "tier": 1, "icon": "🥴", "name": "馬步未穩", "desc": "單月支出首次超過預算"},
    {"code": "save_1",        "tier": 1, "icon": "🧘", "name": "聚氣凝神", "desc": "累計節省超過 $1 元"},
    
    # Level 2 (需完成 Level 1 對應項目)
    {"code": "first_success", "tier": 2, "icon": "🎯", "name": "氣聚丹田", "desc": "單月支出首次低於預算"},
    {"code": "save_300",      "tier": 2, "icon": "🍱", "name": "辟穀修練", "desc": "累計節省超過 $300 元"},
    {"code": "save_1000",     "tier": 2, "icon": "🦸", "name": "丐幫弟子", "desc": "累計節省超過 $1,000 元"},
    {"code": "fail_streak_3", "tier": 2, "icon": "🌪️", "name": "氣息紊亂", "desc": "連續 3 個月支出超標"},

    # Level 3
    {"code": "success_streak_3", "tier": 3, "icon": "🍃", "name": "步履輕盈", "desc": "連續 3 個月支出低於預算"},
    {"code": "save_5000",        "tier": 3, "icon": "🧮", "name": "鐵算盤", "desc": "累計節省超過 $5,000 元"},
    {"code": "fail_streak_6",    "tier": 3, "icon": "🔥", "name": "走火入魔", "desc": "連續 6 個月支出超標"},

    # Level 4
    {"code": "success_streak_6", "tier": 4, "icon": "⛰️", "name": "不動如山", "desc": "連續 6 個月支出低於預算"},
    {"code": "save_10000",       "tier": 4, "icon": "🔔", "name": "金鐘罩頂", "desc": "累計節省超過 $10,000 元"},
    {"code": "super_save",       "tier": 4, "icon": "📜", "name": "守財真經", "desc": "單月節省金額 > 單月總支出"},
]

# --- [關鍵修改 1] 定義前置條件鏈 (Prerequisite Chain) ---
# 格式: "下一級代碼": "上一級代碼"
PREREQUISITES = {
    # 節省系列 (Savings Path)
    "save_300": "save_1",
    "save_1000": "save_300", # 注意：這裡我把 1000 放在 300 後面，依照您的清單順序
    "save_5000": "save_1000",
    "save_10000": "save_5000",
    
    # 成功系列 (Success Streak Path)
    # first_success (首次達標) -> success_streak_3 (連3) -> success_streak_6 (連6)
    "success_streak_3": "first_success",
    "success_streak_6": "success_streak_3",
    
    # 失敗系列 (Fail Streak Path)
    # first_fail -> fail_streak_3 -> fail_streak_6
    "fail_streak_3": "first_fail",
    "fail_streak_6": "fail_streak_3",

    # 特殊成就通常沒有前置，或是獨立線
    "super_save": "success_streak_3" # 假設這是一個高階技巧，需要先學會連3月達標 (您可以依喜好調整)
}

# --- 核心邏輯：檢查並更新成就 ---
def check_and_update_achievements(db: Session):
    # 1. 初始化資料庫
    for ach in INITIAL_ACHIEVEMENTS:
        exists = db.query(models.Achievement).filter_by(code=ach["code"]).first()
        if not exists:
            new_ach = models.Achievement(
                code=ach["code"], name=ach["name"], description=ach["desc"],
                tier=ach["tier"], icon=ach["icon"]
            )
            db.add(new_ach)
    db.commit()

    # 2. 準備數據
    expenses = db.query(models.Expense).all()
    budget_obj = db.query(models.Budget).first()
    monthly_budget = budget_obj.monthly_limit if budget_obj else 30000

    if not expenses:
        return

    # --- [關鍵修改 2] 嚴格的月結算機制 ---
    # 取得「當前年月」字串 (例如 "2026-01")
    current_month_str = date.today().strftime("%Y-%m")
    
    monthly_stats = {}
    for exp in expenses:
        if exp.record_type == "expense":
            m_str = exp.date.strftime("%Y-%m")
            
            # 🛑 守門員：如果這筆帳是「這個月」發生的，為了避免未結算，
            # 我們暫時不把它計入「成就判斷用」的統計數據中。
            # (注意：這不會影響即時記帳顯示，只影響成就計算)
            if m_str == current_month_str:
                continue

            monthly_stats[m_str] = monthly_stats.get(m_str, 0) + exp.amount

    # 排序月份
    sorted_months = sorted(monthly_stats.keys())
    
    # 計算邏輯 (只包含已結算的月份)
    total_savings = 0
    
    streak_over = 0
    streak_under = 0
    max_streak_over = 0
    max_streak_under = 0
    
    has_failed_once = False
    has_succeeded_once = False
    has_super_save = False

    for m in sorted_months:
        spent = monthly_stats[m]
        savings = monthly_budget - spent
        
        if savings > 0:
            total_savings += savings
            has_succeeded_once = True
            streak_under += 1
            streak_over = 0
            
            # 判斷守財真經 (省 > 花)
            if savings > spent:
                has_super_save = True
        else:
            has_failed_once = True
            streak_over += 1
            streak_under = 0
            
        max_streak_under = max(max_streak_under, streak_under)
        max_streak_over = max(max_streak_over, streak_over)

    # --- 3. 逐一解鎖 (含前置檢查) ---
    
    # 先把目前 DB 裡的成就狀態抓出來，做成字典方便查詢 {code: is_unlocked}
    all_db_achs = db.query(models.Achievement).all()
    status_map = {a.code: a.is_unlocked for a in all_db_achs}

    def try_unlock(target_code, condition):
        # 如果條件沒達成，直接跳過
        if not condition:
            return

        # 如果已經解鎖過，也跳過
        if status_map.get(target_code, False):
            return

        # [關鍵修改 3] 檢查前置條件 (Sequential Check)
        parent_code = PREREQUISITES.get(target_code)
        if parent_code:
            # 如果有前置，且前置還沒解鎖 -> 禁止越級打怪
            if not status_map.get(parent_code, False):
                return

        # 通過所有檢查 -> 正式解鎖
        ach_obj = db.query(models.Achievement).filter_by(code=target_code).first()
        ach_obj.is_unlocked = True
        ach_obj.unlocked_at = datetime.now()
        db.commit()
        
        # 更新暫存狀態，讓後面的成就能讀到最新的解鎖狀態 (支援一次解鎖多級)
        status_map[target_code] = True

    # --- 規則判定 ---
    
    # (A) 即時型成就 (不需等待月結算)
    # 只要有記帳就算，不需要等月底
    try_unlock("first_expense", len(expenses) >= 1)

    # (B) 月結算型成就 (使用過濾後的數據)
    try_unlock("save_1", total_savings >= 1)
    try_unlock("save_300", total_savings >= 300)
    try_unlock("save_1000", total_savings >= 1000)
    try_unlock("save_5000", total_savings >= 5000)
    try_unlock("save_10000", total_savings >= 10000)

    try_unlock("first_fail", has_failed_once)
    try_unlock("first_success", has_succeeded_once)
    
    try_unlock("fail_streak_3", max_streak_over >= 3)
    try_unlock("success_streak_3", max_streak_under >= 3)
    
    try_unlock("fail_streak_6", max_streak_over >= 6)
    try_unlock("success_streak_6", max_streak_under >= 6)

    try_unlock("super_save", has_super_save)

@router.get("/", response_model=List[AchievementSchema])
def get_achievements(db: Session = Depends(get_db)):
    check_and_update_achievements(db)
    # 依照等級和 ID 排序
    return db.query(models.Achievement).order_by(models.Achievement.tier, models.Achievement.id).all()

# --- 開發者工具：重置成就 (Backend Only) ---
@router.delete("/reset", status_code=204)
def reset_achievements(db: Session = Depends(get_db)):
    """
    [開發專用] 強制清空成就資料表。
    下次呼叫 GET /achievements/ 時，系統會自動重新初始化並計算。
    """
    # 刪除所有成就紀錄
    db.query(models.Achievement).delete()
    db.commit()
    
    return None