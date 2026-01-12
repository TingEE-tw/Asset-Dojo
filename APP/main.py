from fastapi import FastAPI
from APP.database import engine
from APP import models
from APP.routers import dashboard, expense, stock

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asset Dojo API")

app.include_router(dashboard.router)
app.include_router(expense.router)
app.include_router(stock.router)

@app.get("/")
def read_root():
    return {"message": "系統核心運作中"}