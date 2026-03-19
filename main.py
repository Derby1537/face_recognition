from fastapi import FastAPI
from routers import people_router

app = FastAPI(title="Face recognition API")

app.include_router(router=people_router.router, prefix="/people", tags=["people"])

@app.get("/")
def read_root():
    return {"message": "Server is running"}
