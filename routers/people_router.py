from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import cast, List, Optional
import face_recognition
import pickle
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import or_, String
from db.db import get_db
from models.Person import Person
from models.Picture import Picture
from schemas.person import PersonSchema, PersonUpdate

router = APIRouter()


@router.get("/", response_model=List[PersonSchema])
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

    person_encoding = pickle.loads(cast(bytes, person.encoding))

    pictures = db.query(Picture).all()

    added = 0
    existing_ids = {pic.id for pic in person.pictures}
    for picture in pictures:

        if picture.id in existing_ids:
            continue

        try:
            image = face_recognition.load_image_file(picture.path)
        except Exception:
            continue

        encodings = face_recognition.face_encodings(image)
        if not encodings:
            continue

        for encoding in encodings:
            match = face_recognition.compare_faces(
                [person_encoding],
                encoding,
                tolerance=tolerance
            )[0]

            if match:
                person.pictures.append(picture)
                added += 1
                break

    db.commit()

    return {
        "message": "Sync completed",
        "added_relations": added
    }

@router.get("/{id}", response_model=PersonSchema)
async def getPerson(id: int, db: Session = Depends(get_db)):
    person = db.query(Person)\
        .options(joinedload(Person.pictures))\
        .filter(Person.id == id)\
        .first()

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return person

@router.put("/{id}", response_model=PersonSchema)
async def putPerson(id: int, data: PersonUpdate, db: Session = Depends(get_db)):
    person = db.get(Person, id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    person.name = data.name # type: ignore

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
async def recognizePerson(file: UploadFile = File(...), tolerance: float = 0.5, db: Session = Depends(get_db)):

    people = db.query(Person).all()

    # tieni anche l'oggetto person, non solo il nome
    known_people = []
    known_encodings = []

    for person in people:
        encoding_bytes = cast(bytes, person.encoding)
        known_encodings.append(pickle.loads(encoding_bytes))
        known_people.append(person)

    _ = await file.read()
    try:
        image = face_recognition.load_image_file(file.file)
    except Exception:
        raise HTTPException(status_code=500, detail="Error reading image")

    image_encodings = face_recognition.face_encodings(image)
    if not image_encodings:
        raise HTTPException(status_code=400, detail="No person detected in image")

    results = []

    for target_encoding in image_encodings:
        matches = face_recognition.compare_faces(
            known_encodings, target_encoding, tolerance=tolerance
        )

        matched_results = []

        for i, match in enumerate(matches):
            if match:
                person = known_people[i]

                # recupera tutte le immagini associate
                picture_paths = [pic.path for pic in person.pictures]

                matched_results.append({
                    "name": person.name,
                    "pictures": picture_paths
                })

        if matched_results:
            results.append(matched_results)
        else:
            results.append([{"name": None, "pictures": []}])

    return {"matches": results}       

