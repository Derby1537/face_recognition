import face_recognition
import sys
import pickle
from db.db import engine
from sqlalchemy.orm import sessionmaker
from models.Person import Person

if len(sys.argv) < 2:
    print("Try: python save_encoding.py <filename> <person's name>")
    exit()

image_path = sys.argv[1]

name = " ".join(sys.argv[2:])

image = face_recognition.load_image_file(image_path)
encodings = face_recognition.face_encodings(image)

if not(encodings):
    print(f"No person found in picture {image_path}")
    exit()

encoding = encodings[0]

encoding_blob = pickle.dumps(encoding)

Session = sessionmaker(bind=engine)
session = Session()

person = Person(name=name, encoding=encoding_blob)

session.add(person)
session.commit()
session.close()

print(f"Person {name} saved successfully")
