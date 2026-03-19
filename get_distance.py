import face_recognition
import sys

if len(sys.argv) < 2:
    print("Try python get_distance.py <filename1> <filename2>")
    exit()

image_path_1 = sys.argv[1]
image_path_2 = sys.argv[2]

image_1 = face_recognition.load_image_file(image_path_1)
image_2 = face_recognition.load_image_file(image_path_2)

encodings_1 = face_recognition.face_encodings(image_1)
encodings_2 = face_recognition.face_encodings(image_2)

distance = face_recognition.face_distance(encodings_1, encodings_2[0])

print(f"Distance between \n\t{image_path_1} \nand \n\r{image_path_2}: \n{distance}")
