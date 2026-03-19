from fastapi import APIRouter, UploadFile, File, HTTPException
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
