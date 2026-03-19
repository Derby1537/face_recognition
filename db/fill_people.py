import os
import pickle
import face_recognition
from sqlalchemy.orm import sessionmaker
from db.db import engine
from models.Person import Person
from models.Picture import Picture

# Path della directory LFW
LFW_DIR = "archive/lfw_funneled"

# prepara sessione DB
Session = sessionmaker(bind=engine)
session = Session()

count = 0
MAX_PERSONS = 100  # per esempio, puoi togliere il limite

# scansiona tutte le cartelle nella directory principale
for person_dir in os.listdir(LFW_DIR):
    person_path = os.path.join(LFW_DIR, person_dir)
    if not os.path.isdir(person_path):
        continue  # salta eventuali file

    # lista di tutte le immagini nella cartella
    images = [f for f in os.listdir(person_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not images:
        print(f"Nessuna immagine trovata per {person_dir}, salto...")
        continue

    # prendi il primo volto come encoding per la persona
    first_image_file = os.path.join(person_path, images[0])
    image = face_recognition.load_image_file(first_image_file)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        print(f"Nessun volto trovato in {first_image_file}, salto...")
        continue

    encoding_blob = pickle.dumps(encodings[0])
    person = Person(name=person_dir, encoding=encoding_blob)
    session.add(person)
    session.flush()  # serve per avere subito person.id
    print(f"{person_dir} aggiunto al database con encoding.")

    # salva tutte le immagini come Picture e crea le relazioni
    for img_name in images:
        img_path = os.path.join(person_path, img_name)
        picture = Picture(path=img_path)
        session.add(picture)
        session.flush()  # serve per avere subito picture.id

        # aggiunge relazione many-to-many
        person.pictures.append(picture)

    count += 1
    if count >= MAX_PERSONS:
        break

# conferma tutte le aggiunte
session.commit()
session.close()
print("Database popolato con persone e tutte le immagini collegate!")
