# TOXIC HORIZON

TOXIC HORIZON is a 2D top-down action game built with Python and Arcade.
You play short combat runs, collect scrap, upgrade weapons in the lobby shop,
and survive increasingly stronger enemies.

## Current State

- Playable prototype with menu, tutorial, lobby, combat run, and game-over flow
- Save/load support (autosave + manual JSON files)
- In-game debug console with gameplay commands
- Windows build flow via PyInstaller

## Tech Stack

- Python 3.12
- Arcade 3.3.3
- Tiled TMX maps
- PyInstaller for packaging

## Project Structure

- `scripts/Main.py` -> app entry point and main views
- `scripts/MovementEngine.py` -> movement, dash, shooting, enemy logic, collisions
- `scripts/UIEngine.py` -> HUD, minimap, shop UI, debug console
- `scripts/LoadingScreen.py` -> staged loading for `GameView`
- `scripts/Tutorial.py` -> guided tutorial flow
- `scripts/Data.py` -> runtime data model, weapon table, save/load/autosave
- `scripts/path_utils.py` -> asset path handling (source + PyInstaller runtime)
- `assets/` -> maps, sprites, sounds, tiled config
- `build.ps1` -> Windows build helper script

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run (Dev)

From project root:

```powershell
python scripts/Main.py
```

The game opens in fullscreen using your current display resolution.

## Controls

- `W A S D` -> Move
- `Left Click` -> Shoot
- `Space` -> Dash
- `E` -> Interact (shop/startgame/lobby tiles)
- `Tab` -> Open/close console
- `F3` -> Debug overlay
- `Esc` -> Leave shop or return to menu (from lobby)

## Console Commands

Open console with `Tab`, then enter commands like:

- `/help`
- `/set health 100`
- `/set scrap 500`
- `/set name Survivor`
- `/set weapon 2.1`
- `/set level 3`
- `/enemys spawn`
- `/enemys kill`
- `/overwrite damage 999` or `/overwrite damage default`
- `/overwrite speed 900` or `/overwrite speed default`
- `/volume sound 1`
- `/volume music 1`

## Save System

- Autosave: `autosave.json`
- Manual save/load: file dialogs from the main menu (`SPEICHERN` / `LADEN`)

## Build Windows EXE

Use the provided script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build.ps1
```

The script packages `scripts/Main.py` with assets into a windowed one-file executable.
Output goes to `dist/`.

## Notes

- This project is actively in development.
- UI text and content are mostly German in-game.
- If assets are not found in packaged builds, verify `scripts/path_utils.py` and `--add-data "assets;assets"` in `build.ps1`.
