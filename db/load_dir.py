import os
import pickle
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

import numpy as np
import cv2
from sqlalchemy.orm import sessionmaker
from db.db import engine
from models.Face_Encodings import FaceEncoding
from models.Picture import Picture
from core.face_engine import get_face_app

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
            with open(filepath, "rb") as f:
                contents = f.read()
            is_jpeg = filename.lower().endswith((".jpg", ".jpeg"))
            data = bytes([0xFF, 0xD8, 0xFF]) + contents[3:] if is_jpeg else contents
            arr = np.frombuffer(data, dtype=np.uint8)
            image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if image is None:
                continue
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception:
            continue

        app = get_face_app()
        faces = app.get(image)
        if not faces:
            continue

        for face in faces:
            session.add(FaceEncoding(
                picture_id=picture.id,
                encoding=pickle.dumps(face.embedding)
            ))


load_dir(DIR)

session.commit()
session.close()
print("Done")
