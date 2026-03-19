from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import cast
import face_recognition
import pickle
from sqlalchemy.orm import sessionmaker
from db.db import engine
from models.Person import Person

router = APIRouter()

Session = sessionmaker(bind=engine)

@router.post("/")
async def postPerson(file: UploadFile = File(...), name: str=""):
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    _ = await file.read()
    image = face_recognition.load_image_file(file.file)

    encodings = face_recognition.face_encodings(image)
    if not encodings:
        raise HTTPException(status_code=400, detail="No face detected")

    encoding_blob = pickle.dumps(encodings[0])
    person = Person(name=name, encoding=encoding_blob)

    session = Session()
    session.add(person)
    session.commit()
    session.close()

    return {"message": f"Person {name} created successfully"}

@router.post("/recognize")
async def recognizePerson(file: UploadFile = File(...), tolerance: float = 0.5):
    session = Session()

    people = session.query(Person).all()

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
        session.close()
        raise HTTPException(status_code=500, detail="Error reading image")

    image_encodings = face_recognition.face_encodings(image)
    if not image_encodings:
        session.close()
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

    session.close()

    return {"matches": results}       

