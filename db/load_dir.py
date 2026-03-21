import os
import pickle
import sys
import face_recognition
from sqlalchemy.orm import sessionmaker
from db.db import engine
from models.Face_Encodings import FaceEncoding
from models.Picture import Picture

if len(sys.argv) < 2:
    print("Usage: python -m db.load_dir <dirname>")
    sys.exit(1)

DIR = sys.argv[1]

Session = sessionmaker(bind=engine)
session = Session()

existing_paths = {p for (p,) in session.query(Picture.path).all()}


def load_dir(directory: str):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if os.path.isdir(filepath):
            load_dir(filepath)
            continue

        if not filename.lower().endswith((".jpeg", ".png", ".jpg")):
            continue

        if filepath in existing_paths:
            print(f"Skipping (already loaded): {filepath}")
            continue

        print(f"Loading {filepath}")
        picture = Picture(path=filepath)
        session.add(picture)
        session.flush()

        try:
            image = face_recognition.load_image_file(filepath)
        except Exception:
            continue

        encodings = face_recognition.face_encodings(image)
        if not encodings:
            continue

        for enc in encodings:
            session.add(FaceEncoding(
                picture_id=picture.id,
                encoding=pickle.dumps(enc)
            ))


load_dir(DIR)

session.commit()
session.close()
print("Done")
