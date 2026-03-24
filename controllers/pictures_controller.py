import os
import pickle
import uuid
from typing import List

import numpy as np
import cv2
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session, selectinload

from core.face_engine import get_face_app
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


def _decode_jpeg(data: bytes) -> bytes:
    return bytes([0xFF, 0xD8, 0xFF]) + data[3:]


def _load_image_from_bytes(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def _save_encodings(db: Session, picture_id: int, image: np.ndarray) -> None:
    app = get_face_app()
    faces = app.get(image)
    for face in faces:
        db.add(FaceEncoding(picture_id=picture_id, encoding=pickle.dumps(face.embedding)))


def postPicture(db: Session, path: str) -> PictureBase:
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail="File not found")

    if db.query(Picture).filter(Picture.path == path).first():
        raise HTTPException(status_code=409, detail="Picture already loaded")

    try:
        ext = os.path.splitext(path)[-1].lower()
        with open(path, "rb") as f:
            contents = f.read()
        data = _decode_jpeg(contents) if ext in (".jpg", ".jpeg") else contents
        image = _load_image_from_bytes(data)
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
        data = _decode_jpeg(contents) if ext in (".jpg", ".jpeg") else contents
        image = _load_image_from_bytes(data)
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
