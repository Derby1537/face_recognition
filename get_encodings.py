import sys
import face_recognition

if len(sys.argv) < 2:
    print("Try python get_encodings.py <filename>")
    exit()

image_path = sys.argv[1]

image = face_recognition.load_image_file(image_path)
encodings = face_recognition.face_encodings(image)
landmarks = face_recognition.face_landmarks(image)

i = 1
for encoding in encodings:
    print(f"Encoding person n.{i}: {encoding}")
    print(f"Landmarks person n.{i}: {encoding}")
    i = i+1
