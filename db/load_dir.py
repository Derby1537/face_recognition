import os
import pickle
import sys
import face_recognition
from sqlalchemy.orm import sessionmaker
from db.db import engine
from models.Face_Encodings import FaceEncoding
from models.Picture import Picture

if len(sys.argv) < 2:
    print("Try python fill_pictures.py <dirname>")

DIR = sys.argv[1]

# prepara sessione DB
Session = sessionmaker(bind=engine)
session = Session()

# scansiona tutte le cartelle nella directory principale
for filename in os.listdir(DIR):
    filename_path = os.path.join(DIR, filename)
    if not filename.endswith((".JPEG", ".png", ".jpg")):
        continue
    print(f"Loading {filename}")
    picture = Picture(path=filename_path)
    session.add(picture)
    session.flush()

    try:
        image = face_recognition.load_image_file(filename_path)
    except Exception:
        continue

    encodings = face_recognition.face_encodings(image)
    if not encodings:
        continue

    for enc in encodings:
        encoding_blob = pickle.dumps(enc)

        db_encoding = FaceEncoding(
            picture_id=picture.id,
            encoding=encoding_blob
        )

        session.add(db_encoding)



# conferma tutte le aggiunte
session.commit()
session.close()
print("Database popolato con immagini")
