import os
import pickle
import face_recognition
from sqlalchemy.orm import sessionmaker
from db.db import engine
from models.Person import Person
from models.Picture import Picture

# Path to the LFW dataset directory
LFW_DIR = "archive/lfw_funneled"

# Prepare DB session
Session = sessionmaker(bind=engine)
session = Session()

count = 0
MAX_PERSONS = 100

# Scan all subdirectories in the main directory
for person_dir in os.listdir(LFW_DIR):
    person_path = os.path.join(LFW_DIR, person_dir)
    if not os.path.isdir(person_path):
        continue  # skip files

    # List all images in the folder
    images = [f for f in os.listdir(person_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not images:
        print(f"No images found for {person_dir}, skipping...")
        continue

    # Use the first image as the person's face encoding
    first_image_file = os.path.join(person_path, images[0])
    image = face_recognition.load_image_file(first_image_file)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        print(f"No face found in {first_image_file}, skipping...")
        continue

    encoding_blob = pickle.dumps(encodings[0])
    person = Person(name=person_dir, encoding=encoding_blob)
    session.add(person)
    session.flush()  # get person.id immediately
    print(f"{person_dir} added to database with encoding.")

    # Save all images as Picture and link them to the person
    for img_name in images:
        img_path = os.path.join(person_path, img_name)
        picture = Picture(path=img_path)
        session.add(picture)
        session.flush()  # get picture.id immediately

        person.pictures.append(picture)

    count += 1
    if count >= MAX_PERSONS:
        break

# Commit all additions
session.commit()
session.close()
print("Database populated with people and all linked images!")
