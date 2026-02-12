import json
from tkinter import filedialog, messagebox
import tkinter as tk
from path_utils import asset_path

class DatenManagement:

    def __init__(self):
        self.autosave_path = "autosave.json"
        self._root = tk.Tk() # Keep one instance
        self._root.withdraw() 
        self.setup()
     

    # ---------------------------------------------------------
    # NEUES SPIEL – Daten neu erzeugen
    # ---------------------------------------------------------
    def setup(self):
        self.data = {
            "Username": "",
            "Health": 100,
            "Ultpoints": 0,
            "Schrott": 0,
            "CurrentUlt" : None,
            "Levelnumber": 0,
            "EnemyDevelopement" : 5,
            "CurrentWeapon": "1.1",
            "MusicVolume" : 1,
            "SoundVolume" : 1,
            "PreviousCommands" : [],
            'Maplist' : [asset_path("assets/maps/Map1.tmx"), asset_path("assets/maps/MapNele.tmx")]
        }

        self.weapons = {
            # --- Waffe 1: Kel-Tec P-11 (leichte Pistole) ---
            "1.1": {"sprite": "keltec.png", "name": "Kel-Tec P-11", "speed": 1.20, "damage": 10, "cost": 0,
                    "info": "Leichte Einsteigerpistole. Einfach, zuverlässig, schwach."},
            "1.2": {"sprite": "keltec.png", "name": "Kel-Tec P-11", "speed": 1.15, "damage": 12, "cost": 40,
                    "info": "Verbesserter Abzug und stabilerer Lauf."},
            "1.3": {"sprite": "keltec.png", "name": "Kel-Tec P-11", "speed": 1.10, "damage": 14, "cost": 80,
                    "info": "Maximale Stufe. Schnell und präzise für ihre Klasse."},

            # --- Waffe 2: Glock 19 (mittlere Pistole) ---
            "2.1": {"sprite": "glock.png", "name": "Glock 19", "speed": 1.00, "damage": 16, "cost": 120,
                    "info": "Beliebte Dienstpistole. Gute Balance aus Schaden und Kontrolle."},
            "2.2": {"sprite": "glock.png", "name": "Glock 19", "speed": 0.95, "damage": 20, "cost": 180,
                    "info": "Verbesserte Mechanik, stabilere Schussfolge."},
            "2.3": {"sprite": "glock.png", "name": "Glock 19", "speed": 0.90, "damage": 25, "cost": 250,
                    "info": "Maximale Stufe. Sehr zuverlässig und solide Power."},

            # --- Waffe 3: Desert Eagle (schwere Pistole) ---
            "3.1": {"sprite": "deserteagle.png", "name": "Desert Eagle", "speed": 0.85, "damage": 30, "cost": 300,
                    "info": "Schwere Pistole mit enormem Rückstoß, aber hoher Durchschlagskraft."},
            "3.2": {"sprite": "deserteagle.png", "name": "Desert Eagle", "speed": 0.80, "damage": 35, "cost": 400,
                    "info": "Verbesserter Lauf reduziert Rückstoß und erhöht Präzision."},
            "3.3": {"sprite": "deserteagle.png", "name": "Desert Eagle", "speed": 0.75, "damage": 40, "cost": 550,
                    "info": "Maximale Stufe. Brutale Feuerkraft, jetzt besser kontrollierbar."}
        }
    
    # ---------------------------------------------------------
    # AUTOSAVE – speichert still im Hintergrund
    # ---------------------------------------------------------
    def autosave(self):
        with open(self.autosave_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)

    # ---------------------------------------------------------
    # MANUELLES SPEICHERN (mit Dialog)
    # ---------------------------------------------------------
    def speichern(self):
        self._root.update()

        filepath = filedialog.asksaveasfilename(
            title="Datei speichern unter",
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")]
        )

        if not filepath:
            return False

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)

        messagebox.showinfo("Speichern erfolgreich",
                            f"Spielstand gespeichert unter:\n{filepath}")
        return True

    # ---------------------------------------------------------
    # LADEN
    # ---------------------------------------------------------
    def laden(self):
        self._root.update()

        filepath = filedialog.askopenfilename(
            title="JSON-Datei auswählen",
            filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")]
        )

        if not filepath:
            return False

        with open(filepath, "r", encoding="utf-8") as file:
            self.data = json.load(file)

        messagebox.showinfo("Laden erfolgreich",
                            "Spielstand wurde erfolgreich geladen!")

        self.autosave()
        return True

    # ---------------------------------------------------------
    # DATEN ÄNDERN + AUTOSAVE
    # ---------------------------------------------------------

    def change_data(self, attribute : str, change : int):
        self.data[attribute] += change
        return
        

    def set_data(self, attribute: str, change : int):
        self.data[attribute] = change

    # ---------------------------------------------------------

    def get_alldata(self):
        return self.data
    
    def get_one_data(self, attribute):
        return self.data[attribute]
    
    def get_all_weapon_data(self, Weapon):
        return self.weapons[Weapon]
    
    def get_one_weapon_data(self, Weapon, Attribute):
        return self.weapons[Weapon][Attribute]

    
    def upgrade_weapon(self):
        CurrentWeapon = str(self.data["CurrentWeapon"])
        CurrentLevel = int(CurrentWeapon[-1])
        if CurrentLevel < 3:
            NewWeapon = f"{CurrentWeapon[0]}.{CurrentLevel + 1}"
        else:
            NewWeapon = f"{int(CurrentWeapon[0]) + 1}.1"
        self.data["CurrentWeapon"] = NewWeapon
        self.data["Schrott"] -= self.weapons[NewWeapon]["cost"]

        self.autosave()

    def get_previous_commands(self):
        return self.data["PreviousCommands"]
    
    def append_to_previous_commands(self, newCommand: str):
        if not newCommand.strip():
            return

        self.data["PreviousCommands"].append(newCommand)

        # optionales Limit (empfohlen)
        MAX_HISTORY = 50
        self.data["PreviousCommands"] = self.data["PreviousCommands"][-MAX_HISTORY:]




