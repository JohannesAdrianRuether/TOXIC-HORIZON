# Toxic Horizon – Arcade Game Prototype

Ein 2D‑Top‑Down‑Prototyp basierend auf **Python Arcade**, inklusive:
- Tiled‑Map‑Integration
- Auto‑Movement über Path‑Tiles
- WASD‑Steuerung
- Dash‑Mechanik mit Wand‑Kollisionsprüfung
- JSON‑Speichersystem (Laden/Speichern/Autosave)
- Mehrere Views (Menü, New Game, Base Game)
- Kamera‑Follow‑System

---

## 🚀 Features

### ✔ Tiled‑Map Integration
Die Map wird über eine `.tmx`‑Datei geladen:

- Layer **Walls** → Kollisionen  
- Layer **enemypath** → Auto‑Movement  
- Object‑Layer **Objects** → Spawn‑Positionen  

Tiles aus Tiled werden automatisch zu Arcade‑Sprites mit:
- `center_x`, `center_y`
- `properties`
- `width`, `height`

---

## 🎮 Steuerung

| Taste | Funktion |
|-------|----------|
| **WASD** | Bewegung |
| **SPACE** | Dash in gedrückte Richtung |
| **ESC** | Zurück ins Menü (nur in NewGameView) |

---

## 🧭 Auto‑Movement über Path‑Tiles

Der Layer **enemypath** enthält Tiles mit einer Property:

direction = up / down / left / right


Wenn der Spieler ein solches Tile berührt:

- wird **nur die Richtung gesetzt**
- nicht die Geschwindigkeit verändert

Dadurch bleibt die Bewegung **konstant**, ohne:
- Beschleunigen in der Mitte
- Abbremsen am Übergang
- Ruckeln

---

## ⚡ Dash‑System

Der Dash wird durch **SPACE** ausgelöst und funktioniert nur,
wenn eine Richtung gedrückt wird.

### Anti‑Clip‑System (Swept Collision)
Der Dash wird in **20 kleine Schritte** unterteilt:

- Jeder Schritt prüft Kollision mit Walls
- Wenn ein Schritt kollidiert → Dash wird abgebrochen
- Dadurch ist **kein Durch‑die‑Wand‑Buggen möglich**

---

## 🧱 Kollisionen

### Walls
- Werden über `use_spatial_hash=True` optimiert
- Bewegung wird rückgängig gemacht, wenn eine Wand getroffen wird

### Path‑Tiles
- Beeinflussen nur die Richtung
- Keine Geschwindigkeitsänderung

---

## 👤 Spawn‑System

Der Spieler spawnt über ein Objekt in Tiled:

- Object‑Layer: **Objects**
- Objektname: **player_spawn**

Arcade liest die Position automatisch:

```python
spawn = self.tilemap.object_lists["Objects"][0]
self.Player_sprite.center_x = spawn.x
self.Player_sprite.center_y = spawn.y
