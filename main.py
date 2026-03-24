import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import people_router, pictures_router, stats_router
from dotenv import load_dotenv
from db.db import init_db
from core.face_engine import get_face_app

load_dotenv()

is_production = os.getenv("ENV") == "production"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    get_face_app()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Face recognition API",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
)

app.include_router(router=people_router.router, prefix="/people", tags=["people"])
app.include_router(router=pictures_router.router, prefix="/pictures", tags=["pictures"])
app.include_router(router=stats_router.router, prefix="/stats", tags=["stats"])

@app.get("/")
def read_root():
    return {"message": "Server is running"}
