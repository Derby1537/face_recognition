import face_recognition
import sys

if len(sys.argv) < 2:
    print("Try: python save_encoding.py <filename> <person's name>")
    exit()

image_path = sys.argv[1]

name = sys.argv[2]
for arg in sys.argv[3:]:
    name = name + " " + arg

image = face_recognition.load_image_file(image_path)
encoding = face_recognition.face_encodings(image)[0]

print(encoding)
