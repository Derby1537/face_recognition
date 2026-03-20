from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from models.Picture import Picture
from schemas.picture import PictureBase, PictureWithPeople


def getPictures(db: Session, page: int, page_size: int) -> List[Picture]:
    offset = (page - 1) * page_size
    return db.query(Picture).offset(offset).limit(page_size).all()


def getPicture(db: Session, id: int) -> PictureWithPeople:
    picture = (
        db.query(Picture)
        .options(selectinload(Picture.people))
        .filter(Picture.id == id)
        .first()
    )

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    return picture


def deletePicture(db: Session, id: int) -> dict:
    picture = db.get(Picture, id)

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    db.delete(picture)
    db.commit()

    return {"message": "Picture deleted successfully"}
