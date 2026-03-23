#!/bin/bash

set -e

IMAGE_NAME="face_recognition-api"
OUTPUT="face_recognition-api.tar.gz"

echo "Building Docker image..."
docker compose build

if [ -f "$OUTPUT" ]; then
    echo "Removing old $OUTPUT..."
    rm "$OUTPUT"
fi

echo "Saving image to $OUTPUT..."
docker save "$IMAGE_NAME" | gzip > "$OUTPUT"

echo "Done: $OUTPUT"
