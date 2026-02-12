param(
    [string]$VenvPython = "C:\Users\JohannesARuether\AppData\Local\Programs\Python\Python312\python.exe",
    [string]$Name = "TOXIC HORIZON"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $VenvPython)) {
    throw "Venv Python not found at '$VenvPython'. Activate the venv or pass -VenvPython."
}

& $VenvPython -m PyInstaller `
    --onefile `
    --noconsole `
    --name $Name `
    scripts\Main.py `
    --add-data "assets;assets"


# create build:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\build.ps1