# Build helper for local Windows packaging with PyInstaller.
# This script assumes:
# - Python is installed at the configured path (or passed via -VenvPython)
# - main entry point is scripts\Main.py
# - assets are bundled into the executable as "assets"
param(
    # Absolute path to the Python interpreter used for the build.
    [string]$VenvPython = "C:\Users\JohannesARuether\AppData\Local\Programs\Python\Python312\python.exe",
    # Output executable name.
    [string]$Name = "TOXIC HORIZON"
)

# Stop immediately on any command error so failed builds do not continue silently.
$ErrorActionPreference = "Stop"

# Fail early with a clear message if the configured interpreter does not exist.
if (-not (Test-Path $VenvPython)) {
    throw "Venv Python not found at '$VenvPython'. Activate the venv or pass -VenvPython."
}

# Package the game as a single, windowed executable.
# --onefile: bundles everything into one EXE
# --noconsole: hides terminal window for GUI app
# --add-data "assets;assets": include local assets folder in bundle
& $VenvPython -m PyInstaller `
    --onefile `
    --noconsole `
    --name $Name `
    scripts\Main.py `
    --add-data "assets;assets"


# create build:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\build.ps1
