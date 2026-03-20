import multiprocessing
import uvicorn

if __name__ == "__main__":
    multiprocessing.freeze_support()  # required for Windows
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)
