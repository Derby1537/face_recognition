import faiss
import numpy as np
import pickle
from db.db import SessionLocal
from models.Face_Encodings import FaceEncoding

FAISS_INDEX = None
FAISS_METADATA = []


def build_index():
    global FAISS_INDEX, FAISS_METADATA

    db = SessionLocal()

    rows = db.query(FaceEncoding).all()

    encodings = []
    metadata = []

    for row in rows:
        enc = pickle.loads(row.encoding)
        encodings.append(enc)
        metadata.append({
            "person_id": row.person_id,
            "picture_id": row.picture_id
        })

    db.close()

    if not encodings:
        print("No encodings found")
        return

    encodings_np = np.array(encodings, dtype="float32")

    dimension = 128
    index = faiss.IndexFlatL2(dimension)
    index.add(encodings_np) # type: ignore

    FAISS_INDEX = index
    FAISS_METADATA = metadata

    print(f"FAISS index built with {len(encodings)} encodings")



