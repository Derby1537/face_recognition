#!/bin/bash
set -e

source myvenv/bin/activate
pyinstaller face_recognition_app.spec --noconfirm

echo "Build complete: dist/face_recognition/face_recognition"
