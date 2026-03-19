from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASS = os.getenv("DATABASE_PASS")
DATABASE_HOST = os.getenv("DATABASE_HOST")

server_engine = create_engine(f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}")

with server_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
    print(f"Database {DATABASE_NAME} created successfully")
