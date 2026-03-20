from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session
from db.db import get_db
from models.Picture import Picture
from schemas.picture import PictureSchema

router = APIRouter()

@router.get("/", response_model=List[PictureSchema])
async def getPictures(db: Session = Depends(get_db)):
    pictures = db.query(Picture).all()

    return pictures

@router.get("/{id}", response_model=PictureSchema)
async def getPicture(id: int, db: Session = Depends(get_db)):
    picture = db.query(Picture)\
        .options(joinedload(Picture.people))\
        .filter(Picture.id == id)\
        .first()

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    return picture


@router.delete("/{id}")
async def deletePicture(id: int, db: Session = Depends(get_db)):
    picture = db.get(Picture, id)

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    db.delete(picture)
    db.commit()

    return {"message": "Picture deleted successfully"}


