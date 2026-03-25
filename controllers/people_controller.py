import os
import pickle
from typing import List, Optional, cast

import numpy as np
import cv2
from fastapi import HTTPException, UploadFile
from sqlalchemy import String, or_
from sqlalchemy.orm import Session, selectinload

from core.face_engine import get_face_app
from models.Face_Encodings import FaceEncoding
from models.Person import Person
from models.Picture import Picture
from schemas.person import PersonWithPictures
from schemas.picture import PictureWithTolerance


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _load_image_from_bytes(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)



def getPeople(
    db: Session,
    search: Optional[str],
    id: Optional[int],
    name: Optional[str],
    page: int,
    page_size: int,
) -> List[PersonWithPictures]:
    query = db.query(Person)

    if id is not None:
        query = query.filter(Person.id == id)

    if name:
        query = query.filter(Person.name.ilike(f"%{name}%"))

    if search:
        query = query.filter(
            or_(
                Person.name.ilike(f"%{search}%"),
                Person.id.cast(String).ilike(f"%{search}%"),
            )
        )

    offset = (page - 1) * page_size
    people = (
        query
        .options(selectinload(Person.face_encodings).selectinload(FaceEncoding.picture))
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return [
        PersonWithPictures(
            id=cast(int, p.id),
            name=cast(str, p.name),
            pictures=[
                PictureWithTolerance(id=enc.picture.id, path=enc.picture.path, tolerance=enc.tolerance)
                for enc in p.face_encodings
                if enc.picture is not None
            ],
        )
        for p in people
    ]


def getPerson(db: Session, id: int) -> PersonWithPictures:
    person = (
        db.query(Person)
        .options(selectinload(Person.face_encodings).selectinload(FaceEncoding.picture))
        .filter(Person.id == id)
        .first()
    )
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return PersonWithPictures(
        id=cast(int, person.id),
        name=cast(str, person.name),
        pictures=[
            PictureWithTolerance(id=enc.picture.id, path=enc.picture.path, tolerance=enc.tolerance)
            for enc in person.face_encodings
            if enc.picture is not None
        ],
    )


def putPerson(db: Session, id: int, name: str) -> Person:
    person = db.get(Person, id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    person.name = name  # type: ignore

    db.commit()
    db.refresh(person)

    return person


async def postPerson(db: Session, file: UploadFile, name: str, sync: bool = False, tolerance: float = 0.5) -> dict:
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    contents = await file.read()
    ext = os.path.splitext(file.filename or "")[-1].lower()
    fixed = bytes([0xFF, 0xD8, 0xFF]) + contents[3:] if ext in (".jpg", ".jpeg") else contents
    image = _load_image_from_bytes(fixed)

    app = get_face_app()
    faces = app.get(image)
    if not faces:
        raise HTTPException(status_code=400, detail="No face detected")

    encoding_blob = pickle.dumps(faces[0].embedding)
    person = Person(name=name, encoding=encoding_blob)

    db.add(person)
    db.commit()
    db.refresh(person)

    if sync:
        sync_result = syncPictures(db, cast(int, person.id), tolerance)
        return {"message": f"Person {name} created successfully", "sync": sync_result}

    return {"message": f"Person {name} created successfully"}


async def recognizePerson(db: Session, file: UploadFile, tolerance: float = 0.5, match_all: bool = False) -> dict:
    contents = await file.read()
    ext = os.path.splitext(file.filename or "")[-1].lower()
    fixed = bytes([0xFF, 0xD8, 0xFF]) + contents[3:] if ext in (".jpg", ".jpeg") else contents

    try:
        image = _load_image_from_bytes(fixed)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image")

    app = get_face_app()
    faces = app.get(image)
    if not faces:
        raise HTTPException(status_code=400, detail="No face detected")

    query_embeddings = [face.embedding for face in faces]
    threshold = 1.0 - tolerance

    encodings_db = (
        db.query(FaceEncoding)
        .options(selectinload(FaceEncoding.picture))
        .filter(FaceEncoding.picture_id.isnot(None))
        .all()
    )

    # For each face in the input, collect the set of picture_ids that contain a matching face
    picture_sets: list[set[int]] = []
    for query_embedding in query_embeddings:
        matched: set[int] = set()
        for enc in encodings_db:
            enc_embedding = pickle.loads(cast(bytes, enc.encoding))
            if _cosine_similarity(enc_embedding, query_embedding) >= threshold:
                matched.add(cast(int, enc.picture_id))
        picture_sets.append(matched)

    if not picture_sets:
        return {"matches": []}

    if match_all:
        result_ids = picture_sets[0]
        for s in picture_sets[1:]:
            result_ids = result_ids & s
    else:
        result_ids: set[int] = set()
        for s in picture_sets:
            result_ids = result_ids | s

    pictures = db.query(Picture).filter(Picture.id.in_(result_ids)).all()
    return {
        "matches": [
            {"picture_id": cast(int, pic.id), "filename": os.path.basename(cast(str, pic.path))}
            for pic in pictures
        ]
    }


def unlinkEncoding(db: Session, person_id: int, encoding_id: int) -> dict:
    encoding = db.query(FaceEncoding).filter(
        FaceEncoding.id == encoding_id,
        FaceEncoding.person_id == person_id
    ).first()
    if not encoding:
        raise HTTPException(status_code=404, detail="Encoding not found")

    encoding.person_id = None
    encoding.tolerance = None
    db.commit()

    return {"message": "Encoding unlinked successfully"}


def deletePerson(db: Session, id: int) -> dict:
    person = db.get(Person, id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    db.query(FaceEncoding).filter(FaceEncoding.person_id == id).update(
        {FaceEncoding.person_id: None, FaceEncoding.tolerance: None}
    )

    db.delete(person)
    db.commit()

    return {"message": "Person deleted successfully"}


def syncPictures(db: Session, id: int, tolerance: float) -> dict:
    person = db.get(Person, id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Reset only encodings assigned to this person with a higher (less precise) tolerance
    db.query(FaceEncoding).filter(
        FaceEncoding.person_id == id,
        FaceEncoding.tolerance > tolerance
    ).update({FaceEncoding.person_id: None, FaceEncoding.tolerance: None})
    db.commit()

    person_encoding = pickle.loads(cast(bytes, person.encoding))
    threshold = 1.0 - tolerance

    # Only consider encodings that are unassigned or assigned to this person with worse tolerance
    encodings = db.query(FaceEncoding).filter(
        (FaceEncoding.person_id == None) |
        (FaceEncoding.person_id == id)
    ).all()
    updated = 0

    for db_encoding in encodings:
        # Skip encodings already assigned to this person with a better (lower) tolerance
        if db_encoding.person_id == id and db_encoding.tolerance is not None and db_encoding.tolerance <= tolerance:
            continue

        encoding = pickle.loads(cast(bytes, db_encoding.encoding))
        similarity = _cosine_similarity(person_encoding, encoding)

        if similarity >= threshold:
            db_encoding.person_id = id
            db_encoding.tolerance = tolerance
            updated += 1

    db.commit()

    return {"message": "Sync completed", "updated_encodings": updated}


