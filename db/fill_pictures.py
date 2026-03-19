import os
from sqlalchemy.orm import sessionmaker
from db.db import engine
from models.Picture import Picture

# Path della directory LFW
DIR = "archive/Carmelo"

# prepara sessione DB
Session = sessionmaker(bind=engine)
session = Session()

# scansiona tutte le cartelle nella directory principale
for filename in os.listdir(DIR):
    filename_path = os.path.join(DIR, filename)
    # if not os.path.isdir(filename_path):
    #     continue  # salta eventuali file

    # lista di tutte le immagini nella cartella
    # images = [f for f in os.listdir(person_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    # if not images:
    #     print(f"Nessuna immagine trovata per {person_dir}, salto...")
    #     continue

    picture = Picture(path=filename_path)
    session.add(picture)
    session.flush()  # serve per avere subito picture.id



# conferma tutte le aggiunte
session.commit()
session.close()
print("Database popolato con immagini")
