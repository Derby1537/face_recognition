import face_recognition
import os
from fastapi import FastAPI, UploadFile, File
import shutil

app = FastAPI()

DATASET_DIR = "archive/dataset"

# 🔹 Precarica encoding dataset (IMPORTANTISSIMO per performance)
known_encodings = []
known_filenames = []

for filename in os.listdir(DATASET_DIR):
    if filename.endswith((".jpg", ".png")):
        path = os.path.join(DATASET_DIR, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_encodings.append(encodings[0])
            known_filenames.append(filename)

print(f"Caricate {len(known_encodings)} immagini nel dataset")


@app.post("/match")
async def match_face(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"

    # salva temporaneamente il file
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # carica immagine
    image = face_recognition.load_image_file(temp_path)
    encodings = face_recognition.face_encodings(image)

    os.remove(temp_path)

    if not encodings:
        return {"error": "Nessun volto trovato"}

    target_encoding = encodings[0]

    results = []

    for i, known_encoding in enumerate(known_encodings):
        match = face_recognition.compare_faces(
            [known_encoding],
            target_encoding,
            tolerance=0.5
        )

        if match[0]:
            results.append(known_filenames[i])

    return {
        "matches": results,
        "count": len(results)
    }
