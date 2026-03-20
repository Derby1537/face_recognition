from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers import pictures_controller
from db.db import get_db
from schemas.picture import PictureBase, PictureWithPeople

router = APIRouter()


@router.get("/", response_model=List[PictureBase])
async def getPictures(page: int = 1, page_size: int = 25, db: Session = Depends(get_db)):
    page_size = min(page_size, 100)
    return pictures_controller.getPictures(db, page, page_size)


@router.get("/{id}", response_model=PictureWithPeople)
async def getPicture(id: int, db: Session = Depends(get_db)):
    return pictures_controller.getPicture(db, id)

@router.post("/", response_model=PictureBase)
async def postPicture(path: str, db: Session = Depends(get_db)):
    return pictures_controller.postPicture(db, path)


@router.delete("/{id}")
async def deletePicture(id: int, db: Session = Depends(get_db)):
    return pictures_controller.deletePicture(db, id)
