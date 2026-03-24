# Run with: .\build_windows.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

& "myvenv\Scripts\Activate.ps1"
.\myvenv\Scripts\pyinstaller.exe face_recognition_app.spec --noconfirm

Write-Host "Copying .env..."
Copy-Item ".env" "dist\face_recognition\.env"

Write-Host "Copying ai_models..."
Copy-Item -Recurse "ai_models" "dist\face_recognition\ai_models"

Write-Host "Build complete: dist\face_recognition\face_recognition.exe"
