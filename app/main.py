from fastapi import FastAPI
from app.database import init_db
from app.routes import orders

app = FastAPI(title="Cronck API")


# taskkill /PID 10416 /F
# netstat -ano | findstr :8080
# uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
# http://127.0.0.1:8080/docs#/
# pip install -r requirements.txt

@app.on_event("startup")
async def startup():
    await init_db()


app.include_router(orders.router)


@app.get("/")
async def root():
    return {"message": "API is running!"}
