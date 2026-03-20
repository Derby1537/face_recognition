import os
import pickle
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

import face_recognition
from models.Face_Encodings import FaceEncoding
from models.Picture import Picture
from schemas.picture import PictureWithPeople


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


def postPicture(db: Session, path: str) -> Picture:
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail="File not found")

    existing = db.query(Picture).filter(Picture.path == path).first()
    if existing:
        raise HTTPException(status_code=409, detail="Picture already loaded")

    try:
        image = face_recognition.load_image_file(path)
    except Exception:
        raise HTTPException(status_code=400, detail="Error opening image")

    picture = Picture(path=path)
    db.add(picture)
    db.flush()

    encodings = face_recognition.face_encodings(image)
    for encoding in encodings:
        db.add(FaceEncoding(picture_id=picture.id, encoding=pickle.dumps(encoding)))

    db.commit()
    db.refresh(picture)

    return picture


def deletePicture(db: Session, id: int) -> dict:
    picture = db.get(Picture, id)

    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    db.delete(picture)
    db.commit()

    return {"message": "Picture deleted successfully"}
