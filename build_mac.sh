#!/bin/bash
set -e

source myvenv/bin/activate
pyinstaller face_recognition_app.spec --noconfirm

echo "Copying .env..."
cp .env dist/face_recognition/.env

echo "Copying ai_models..."
cp -r ai_models dist/face_recognition/ai_models

echo "Build complete: dist/face_recognition/face_recognition"
