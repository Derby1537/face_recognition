import io
import os
import pickle
import uuid
from typing import List

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session, selectinload

import face_recognition
from models.Face_Encodings import FaceEncoding
from models.Picture import Picture
from schemas.picture import PictureBase, PictureWithPeople

UPLOAD_DIR = os.path.join("public", "image")


def getPictures(db: Session, page: int, page_size: int) -> List[PictureBase]:
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


def _decode_jpeg(data: bytes) -> io.BytesIO:
    fixed = bytes([0xFF, 0xD8, 0xFF]) + data[3:]
    return io.BytesIO(fixed)


def _save_encodings(db: Session, picture_id: int, image) -> None:
    encodings = face_recognition.face_encodings(image)
    for encoding in encodings:
        db.add(FaceEncoding(picture_id=picture_id, encoding=pickle.dumps(encoding)))


def postPicture(db: Session, path: str) -> PictureBase:
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail="File not found")

    if db.query(Picture).filter(Picture.path == path).first():
        raise HTTPException(status_code=409, detail="Picture already loaded")

    try:
        ext = os.path.splitext(path)[-1].lower()
        with open(path, "rb") as f:
            contents = f.read()
        src = _decode_jpeg(contents) if ext in (".jpg", ".jpeg") else io.BytesIO(contents)
        image = face_recognition.load_image_file(src)
    except Exception:
        raise HTTPException(status_code=400, detail="Error opening image")

    picture = Picture(path=path)
    db.add(picture)
    db.flush()

    _save_encodings(db, picture.id, image)

    db.commit()
    db.refresh(picture)

    return picture


async def uploadPicture(db: Session, file: UploadFile) -> PictureBase:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in (".jpg", ".jpeg", ".png"):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    with open(path, "wb") as f:
        f.write(contents)

    if db.query(Picture).filter(Picture.path == path).first():
        raise HTTPException(status_code=409, detail="Picture already loaded")

    try:
        src = _decode_jpeg(contents) if ext in (".jpg", ".jpeg") else io.BytesIO(contents)
        image = face_recognition.load_image_file(src)
    except Exception:
        os.remove(path)
        raise HTTPException(status_code=400, detail="Error opening image")

    picture = Picture(path=path)
    db.add(picture)
    db.flush()

    _save_encodings(db, picture.id, image)

    db.commit()
    db.refresh(picture)

    return picture


def deletePicture(db: Session, id: int) -> dict:
    picture = db.get(Picture, id)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    db.query(FaceEncoding).filter(FaceEncoding.picture_id == id).delete()
    db.delete(picture)
    db.commit()

    return {"message": "Picture deleted successfully"}
