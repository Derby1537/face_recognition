import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASS = os.getenv("DATABASE_PASS")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")

DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}/{DATABASE_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
