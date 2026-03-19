from fastapi import APIRouter
from sqlalchemy.orm import sessionmaker
from db.db import engine

router = APIRouter()

Session = sessionmaker(bind=engine)

