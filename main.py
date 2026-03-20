from fastapi import FastAPI
from routers import people_router, pictures_router
# from FAISS.faiss_index import build_index

app = FastAPI(title="Face recognition API")

app.include_router(router=people_router.router, prefix="/people", tags=["people"])
app.include_router(router=pictures_router.router, prefix="/pictures", tags=["pictures"])

# @app.on_event("startup")
# def startup_event():
#     build_index()
#
# @app.post("/rebuild_index")
# def rebuild_index():
#     build_index()
#     return {"message": "Index built successfully"}

@app.get("/")
def read_root():
    return {"message": "Server is running"}
