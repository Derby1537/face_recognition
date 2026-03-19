import face_recognition
import os
import sys

if len(sys.argv) < 2:
    print("Try: python main.py <filename>")
    exit()

target_image_path = sys.argv[1]

target_image = face_recognition.load_image_file(target_image_path)
target_encodings = face_recognition.face_encodings(target_image)

if len(target_encodings) == 0:
    print("No face recognized")
    exit()

image_dir = os.path.join("archive", "dataset")

target_encoding = target_encodings[0]

count = 0
for filename in os.listdir(image_dir):
    count = count + 1
    if count % 1000 == 0:
        print(f"Checked {count}/{len(os.listdir(image_dir))} images")
    if filename.endswith((".jpg", ".png")):
        path = os.path.join(image_dir, filename)

        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        for encoding in encodings:
            match = face_recognition.compare_faces([target_encoding], encoding, tolerance=0.5)
            if match[0] == True:
                print(f"Target person found in image {filename}")
                break

print(f"Checked all images")
