import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

if getattr(sys, 'frozen', False):
    load_dotenv(os.path.join(os.path.dirname(sys.executable), '.env'))
else:
    load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASS = os.getenv("DATABASE_PASS")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")

DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}/{DATABASE_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL)


def init_db():
    base_url = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}?charset=utf8mb4"
    base_engine = create_engine(base_url)

    with base_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))

    base_engine.dispose()

    from models import Base
    Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
