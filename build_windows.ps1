# Run with: .\build_windows.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

& "myvenv\Scripts\Activate.ps1"
pyinstaller face_recognition_app.spec --noconfirm

Write-Host "Build complete: dist\face_recognition\face_recognition.exe"
