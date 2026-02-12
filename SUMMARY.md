# TOXIC HORIZON - Projektzusammenfassung

## 1) Projektziel
**TOXIC HORIZON** ist ein 2D-Topdown-Actionspiel auf Basis von `arcade` (Python), mit:
- Start-/Menü-/Lobby-/Tutorial-/GameOver-Views
- Kampfsystem (Schießen, Dash, Gegner-KI)
- Minimap, Shop, Konsole/Cheat-Commands
- Speichern/Laden (JSON)
- Packaging als Windows-EXE via PyInstaller

---

## 2) Tech-Stack
- Sprache: **Python 3.12**
- Engine: **arcade 3.3.3**
- Rendering/Input: `arcade`, `pyglet`
- Maps: Tiled-TMX via `arcade.load_tilemap` / `pytiled_parser`
- Build: `pyinstaller`
- Persistenz: JSON (`autosave.json` + manuelle Save/Load-Dialoge via `tkinter`)

Abhängigkeiten stehen in `requirements.txt`.

---

## 3) Projektstruktur
- `scripts/Main.py`: Einstieg + zentrale Views (`MenuView`, `NewGameView`, `LobbyView`, `GameView`, `GameOver`, `StartUp`)
- `scripts/MovementEngine.py`: Bewegung, Dash, Gegner-Spawn/KI, Schüsse, Kollisionen, Loot
- `scripts/UIEngine.py`: HUD, Minimap, Debug, Shop-UI, Ingame-Konsole
- `scripts/LoadingScreen.py`: gestuftes Vorladen der `GameView`-Ressourcen
- `scripts/Tutorial.py`: Tutorial-View mit Phasen/Dialogen
- `scripts/Data.py`: Datenmodell, Autosave, Save/Load, Waffen-Upgrades
- `scripts/path_utils.py`: runtime-sichere Asset-Auflösung (Source + PyInstaller onefile)
- `scripts/miris_wiki.html`: Wiki/Help-Seite (wird aus dem Menü geöffnet)
- `assets/`: komplette Spielressourcen (Sprites, Sounds, Maps)
- `build.ps1`: Build-Skript für PyInstaller
- `TOXIC HORIZON.spec`: PyInstaller-Spec-Datei
- `autosave.json`: aktueller Spielstand
- `build/`, `dist/`: Build-Ausgaben

---

## 4) Laufzeit-Architektur (High-Level)
1. `main()` erstellt ein fullscreen `arcade.Window`.
2. `StartUp` zeigt Intro (Sound + Logo) und wechselt dann ins Menü.
3. `MenuView` steuert:
- Neues Spiel
- Laden/Speichern
- Tutorial
- Wiki
- Exit
4. `LobbyView` ist der Hub:
- Bewegung
- Shop-Interaktion
- Start in eigentlichen Kampf (`GameView`)
5. `LoadingScreen` baut `GameView`-Objekte vor (Map, Szene, Sprites, Engines, UI).
6. `GameView` läuft mit:
- `MovementEngine` für Gameplay-Logik
- `UIEngine` für HUD/Minimap/Console
7. Bei Tod folgt `GameOver`.

---

## 5) Kern-Gameplay

### Player & Steuerung
- Bewegung: `W/A/S/D`
- Dash: `SPACE` (mit Cooldown)
- Schießen: Linksklick
- Interaktion: `E` (bei Interaction-Tiles)
- Konsole: `TAB`
- Debug-Overlay: `F3`
- Escape-Kontext: Menü/Shop schließen

### Gegnerlogik
- Gegner werden über Spawn-Tiles geladen.
- Es gibt mindestens zwei Verhaltenstypen:
- Follower (verfolgen den Spieler)
- Path-Gegner (patrouillieren auf Pfad-Tiles, können aggro wechseln)
- Bei niedrigem HP-Stand erhöhen Gegner ihr Aggro-/Tempoverhalten.

### Kampfsystem
- Waffendaten kommen aus `Data.py` (Stufen 1.1 bis 3.3).
- Feuerrate + Schaden hängen von aktiver Waffe ab.
- Trefferprüfung via Sprite-Kollisionen.
- Gegner droppen Schrott (Loot), der für Upgrades genutzt wird.

---

## 6) UI-System
`UIEngine` liefert:
- HP-/Schrott-/Level-/Ult-Anzeige
- Dash-Statusvisualisierung
- Minimap-Rendering (Texture/FBO-basiert)
- Debug-Infos (Zeit/FPS)
- Ingame-Konsole mit Commands
- Shop-Layout mit Upgrade-Buttons und Waffenvorschau

---

## 7) Datenmodell & Persistenz
`DatenManagement` hält:
- Spielername, HP, Schrott, Level
- Waffenstand und Waffentabelle
- Lautstärke-Werte
- Command-History
- Mapliste

Persistenz:
- Automatisch: `autosave.json`
- Manuell: `speichern()` / `laden()` über Dateidialoge

---

## 8) Asset- und Pfad-Handling
Wichtiges Architekturdetail:
- Alle Asset-Zugriffe laufen über `asset_path(...)` (`scripts/path_utils.py`).
- Dadurch funktionieren Pfade sowohl:
- im normalen Source-Run
- als `PyInstaller --onefile` Build (über `sys._MEIPASS`)

Dieses Fixing verhindert typische Fehler wie:
`FileNotFoundError ... dist\assets\...`

---

## 9) Build & Distribution
Build mit `build.ps1`:
- nutzt konfigurierten Python-Interpreter
- baut mit PyInstaller als `--onefile --noconsole`
- bindet Assets ein: `--add-data "assets;assets"`

Ergebnis:
- EXE unter `dist/`

---

## 10) Aktueller Stand / ToDo-Kontext
Laut `README.md` sind offene Themen u. a.:
- weitere Grafik-/Pixel-Arbeiten
- Sound-Erweiterungen (Lobby/Game/UI/FX)
- UI-Lautstärkeoptionen
- benutzerfreundlichere Console-Befehle

---

## 11) Fazit
Das Projekt ist bereits als spielbarer Arcade-Loop aufgebaut und modular getrennt:
- View-Flow in `Main.py`
- Gameplay-Logik in `MovementEngine.py`
- UI in `UIEngine.py`
- Daten in `Data.py`

Mit dem vorhandenen Build-Prozess und dem robusten Asset-Pfadhandling ist der Code sowohl lokal als auch als EXE gut nutzbar und erweiterbar.
