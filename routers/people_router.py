import pickle
from typing import List, Optional, cast

import numpy as np
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import String, or_
from sqlalchemy.orm import Session, selectinload

import face_recognition
import FAISS.faiss_index as faiss_index
from db.db import get_db
from models.Face_Encodings import FaceEncoding
from models.Person import Person
from schemas.person import PersonBase, PersonUpdate, PersonWithPictures

router = APIRouter()


@router.get("/", response_model=List[PersonBase])
async def getPeople(
    search: Optional[str] = None,
    id: Optional[int] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
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

    people = query.all()
    return people

@router.post("/sync_pictures")
async def syncPictures(
    id: int, 
    tolerance: float = 0.5, 
    db: Session = Depends(get_db)
):
    person = db.get(Person, id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    db.query(FaceEncoding).filter(FaceEncoding.person_id == id).delete()
    db.commit()
    
    person_encoding = pickle.loads(cast(bytes, person.encoding))

    encodings = db.query(FaceEncoding).all()
    updated = 0

    for db_encoding in encodings:
        encoding = pickle.loads(cast(bytes, db_encoding.encoding))
        match = face_recognition.compare_faces([person_encoding], encoding, tolerance=tolerance)[0]

        if match:
            db_encoding.person_id = id
            db_encoding.tolerance = tolerance
            updated += 1

    db.commit()

    return {
        "message": "Sync completed",
        "updated_encodings": updated
    }

@router.get("/{id}", response_model=PersonWithPictures)
async def getPerson(id: int, db: Session = Depends(get_db)):
    person = (
        db.query(Person)
        .options(selectinload(Person.pictures))
        .filter(Person.id == id)
        .first()
    )

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return person

@router.put("/{id}", response_model=PersonBase)
async def putPerson(id: int, data: PersonUpdate, db: Session = Depends(get_db)):
    person = db.get(Person, id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    person.name = data.name  # type: ignore

    db.commit()
    db.refresh(person)

    return person

@router.post("/")
async def postPerson(file: UploadFile = File(...), name: str="", db: Session = Depends(get_db)):
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    _ = await file.read()
    image = face_recognition.load_image_file(file.file)

    encodings = face_recognition.face_encodings(image)
    if not encodings:
        raise HTTPException(status_code=400, detail="No face detected")

    encoding_blob = pickle.dumps(encodings[0])
    person = Person(name=name, encoding=encoding_blob)

    db.add(person)
    db.commit()

    return {"message": f"Person {name} created successfully"}

@router.post("/recognize")
async def recognizePerson(file: UploadFile = File(...), tolerance: float = 0.5):

    if faiss_index.FAISS_INDEX is None:
        raise HTTPException(status_code=500, detail="FAISS not initialized")

    _ = await file.read()

    try:
        image = face_recognition.load_image_file(file.file)
    except Exception:
        raise HTTPException(status_code=500, detail="Error reading image")

    image_encodings = face_recognition.face_encodings(image)
    if not image_encodings:
        raise HTTPException(status_code=400, detail="No person detected")

    results = []

    for enc in image_encodings:
        query = np.array([enc/np.linalg.norm(enc)], dtype="float32") 

        k = faiss_index.FAISS_INDEX.ntotal
        D, I = faiss_index.FAISS_INDEX.search(query, k=k) # type: ignore

        matches = []

        for idx, dist in zip(I[0], D[0]):
            if idx == -1:
                continue

            if dist < tolerance:
                data = faiss_index.FAISS_METADATA[idx]
                matches.append({ 
                    "person_id": id,
                    "picture_id": data["picture_id"] 
                })

        results.append(matches if matches else [None])

    return {"matches": results}
