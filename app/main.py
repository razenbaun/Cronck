from click.core import batch
from fastapi import FastAPI
from app.database import init_db
from app.routes import (orders, batches, equipment, workers,
                        winding, extrusion, cutting, paketki,
                        printing, flexa, fproducts
                        )

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
app.include_router(batches.router)
app.include_router(equipment.router)
app.include_router(workers.router)
app.include_router(winding.router)
app.include_router(extrusion.router)
app.include_router(cutting.router)
app.include_router(paketki.router)
app.include_router(printing.router)
app.include_router(flexa.router)
app.include_router(fproducts.router)



@app.get("/")
async def root():
    return {"message": "API is running!"}
