from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers import stats_controller
from db.db import get_db

router = APIRouter()


@router.get("/")
def getStats(db: Session = Depends(get_db)):
    return stats_controller.getStats(db)
