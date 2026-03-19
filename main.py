from fastapi import FastAPI
from routers import people_router, pictures_router

app = FastAPI(title="Face recognition API")

app.include_router(router=people_router.router, prefix="/people", tags=["people"])
app.include_router(router=pictures_router.router, prefix="/pictures", tags=["pictures"])

@app.get("/")
def read_root():
    return {"message": "Server is running"}
