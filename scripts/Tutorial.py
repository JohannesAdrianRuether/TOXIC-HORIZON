import arcade
from Main import *
import time
import Data
from path_utils import asset_path
Daten = Data.DatenManagement()

class Tutorial(arcade.View):
    def __init__(self):
        super().__init__()
        Daten.autosave()
        Daten.set_data("Username", "Überlebender")
        self.tilemap = arcade.load_tilemap(asset_path("assets/maps/TutorialMap.tmx"), scaling=2, layer_options={"Walls": {"use_spatial_hash": True}})
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.Player_sprite = arcade.Sprite()
        self.Player_sprite.scale = 0.5

        # Walk only
        self.player_walk_right = [
            arcade.load_texture(asset_path("assets/sprites/player/walk_right_1.png")),
            arcade.load_texture(asset_path("assets/sprites/player/walk_right_1.png")),
            arcade.load_texture(asset_path("assets/sprites/player/walk_right_1.png")),
        ]

        self.player_walk_left = [
            arcade.load_texture(asset_path("assets/sprites/player/walk_left_1.png")),
            arcade.load_texture(asset_path("assets/sprites/player/walk_left_1.png")),
            arcade.load_texture(asset_path("assets/sprites/player/walk_left_1.png")),
        ]

        self.player_anim_timer = 0
        self.player_anim_index = 0
        self.player_facing = "right"

        # Starttexture
        self.Player_sprite.texture = self.player_walk_right[0]

      
        
        for spawn in self.scene["spawns"]:
            if spawn.properties.get("spawn") == "player":
                self.Player_sprite.center_x, self.Player_sprite.center_y = spawn.center_x, spawn.center_y

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.GameMovementEngine = MovementEngine(self.scene, self.camera, self.window, Daten)
        self.GameUIEngine = UIEngine(self.window, Daten)
        self.GameMovementEngine.spawn_enemys()

        self.dash_x, self.dash_y = 0, 0
        self.dash_decay, self.dash_cooldown = 1.2, 1.5
        self.keys_down = set()
        self.text_username = arcade.Text(Daten.get_one_data("Username"), 0, 0, arcade.color.WHITE, 15, anchor_x="center")

        self.interactiontiles = self.scene["interactions"]
        self.button_e_sprite = arcade.Sprite(asset_path("assets/sprites/EButton.png"))

        Daten.set_data("Health", 100)
        self.GameUIEngine.minimap_setup()

        


        self.text_weiter = arcade.Text("(ENTER für weiter)", self.window.width//2, 110, arcade.color.BLACK, 12, anchor_x="center", italic=True)
        self.sprite_miro = arcade.Sprite(asset_path("assets/sprites/miro.png"))
        self.sprite_miro.scale = 6
        self.sprite_miro.right = self.window.width - 100
        self.sprite_miro.bottom = 0
        self.phase = 0

        self.text_chatbox = arcade.Text(
            "",
            x=self.window.width//2,
            y=200,
            color=arcade.color.BLACK,
            font_size=20,
            width=700,
            multiline=True,
            anchor_x="center",
            anchor_y="center",
            align="center")
        
        self.phase_text_dict = {
            0: "Lorem ipsum dolor sit amet ... Ähem ... 'tschuldige falscher Text ...",
            1: "…Oh. Ein neuer Überlebender? Ich bin Miro. Keine Sorge ich beiße nicht. :)",
            2: "Willkommen in der Zone. Seit dem Zusammenbruch ist hier alles ein bisschen… chaotisch.",
            3: "Das wichtigste zuerst: Oben link in der Ecke siehst du deine HP und deinen gesammelten Schrot.",
            4: "Darüber siehst du immer eine MiniMap! Falls du dich hier draußen mal verlaufen solltest ... Die RobotterSpinnen (S.P.I.N.N.E.N.) sind rot, die Dronen blau, Du Lila",
            5: "Dein Fluchtpunkt ist grün! Vielleicht musst du ihn manchmal erst suchen. Wenn du deine Arbeit erledigt hast, kann du mit ihm ins Camp zurück kehren um zu leveln.",
            6: "Bevor du rausgehst: Bewegung ist überlebenswichtig. Nutze WASD um dich zu bewegen.",
            7: "Wenn dir etwas zu nahe kommt: Linksklick. Dann schießt du. Zielen musst du selbst.",
            8: "Du kannst auch dashen mit der Leertaste. Unten in der Mitte siehst du deine Dash-Anzeige.",
            9: "Für jeden erledigten Gegner bekommst du Schrott. Schrott ist hier so etwas wie… Währung.",
            10: "Aber ACHTUNG! Fallen die HP des Gegners unter 25% wird er nochmal so richtig sauer!",
            11: "Mit genug Schrott kannst du deine Waffe upgraden. Mehr Schaden, mehr Überleben.",
            12: "Aber Vorsicht: Mit jeder Runde werden die Monster stärker. Sie lernen schnell.",
            13: "Und wenn deine Lebenspunkte auf 0 fallen… nun ja. Dann war's das. Game Over.",
            14: "Manche Orte kannst du untersuchen oder betreten (Shop im Camp und Flucht aus dem Kampfbereich). Wenn du ein Symbol siehst: Drücke E zum Interagieren.",
            15: "Also: Bleib in Bewegung, sammle Schrott, upgrade deine Waffe und überlebe. Bereit? Das war's von mir, viel erfolg dort draußen!",
            16: "Falls du irgendwan mal Hile brauchen solltest, warte ich im Hauptmenü unter >MIRI'S WIKI< auf dich!"
        }

        self.dash_x, self.dash_y = self.GameMovementEngine.player_movement(
                self.Player_sprite, self.keys_down,
                self.dash_x, self.dash_y, self.dash_decay, 0
            )




    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
 
        if self.phase >= 8:
            self.GameUIEngine.Game_draw_enemy_health(self.GameMovementEngine)
            self.GameMovementEngine.draw_enemys()

        self.text_username.draw()
        for interaction in self.interactiontiles:
            if arcade.check_for_collision(interaction, self.Player_sprite):
                interactiontype = interaction.properties.get("interactiontype", None)
                if interactiontype in ["lobby"]:
                    self.button_e_sprite.center_x = self.Player_sprite.center_x
                    self.button_e_sprite.center_y = self.Player_sprite.center_y - 60
                    self.button_e_sprite.alpha = self.GameUIEngine.get_cycle()
                    arcade.draw_sprite(self.button_e_sprite)

        
        arcade.draw_sprite(self.Player_sprite, pixelated=True)
        self.gui_camera.use()

        arcade.draw_sprite(self.sprite_miro, pixelated=True)
        arcade.draw_lbwh_rectangle_filled(self.window.width//2-400, 100, 800, 200, arcade.color.AERO_BLUE)
        self.text_weiter.draw()
        self.text_chatbox.text = self.phase_text_dict[self.phase]
        self.text_chatbox.draw()

        self.GameUIEngine.Game_draw_UI(self.GameMovementEngine, self.dash_cooldown)

        if arcade.key.F3 in self.keys_down:
            self.GameUIEngine.draw_debug()
        
        if time.monotonic() % 20 == 0:
            Daten.autosave()

        if self.playerisdead:
            Daten.autosave()    
            arcade.schedule(lambda dt: self.window.show_view(GameOver()), 0)

    def on_update(self, delta_time):
        self.GameUIEngine.run_cycle()
        self.GameUIEngine.Game_update_UI()
        if self.phase >= 8:
            self.GameMovementEngine.run_enemy_movement(self.Player_sprite)
        self.playerisdead = self.GameMovementEngine.all_collision_checks(self.Player_sprite)
        
        if self.phase >= 7:
            self.dash_x, self.dash_y = self.GameMovementEngine.player_movement(
                self.Player_sprite, self.keys_down,
                self.dash_x, self.dash_y, self.dash_decay, delta_time
            )
            self.text_username.x = self.Player_sprite.center_x
            self.text_username.y = self.Player_sprite.center_y + 55
            self.update_player_animation(delta_time)
        self.GameUIEngine.update_minimap(self.tilemap, self.scene, self.Player_sprite, self.GameMovementEngine.path_Enemy_sprite_list, self.GameMovementEngine.following_Enemy_sprite_list, self.interactiontiles)
        

    def update_player_animation(self, delta_time):
        # Bewegung prüfen
        moving = (
            arcade.key.W in self.keys_down or
            arcade.key.A in self.keys_down or
            arcade.key.S in self.keys_down or
            arcade.key.D in self.keys_down or
            self.dash_x != 0 or self.dash_y != 0
        )

        # Richtung bestimmen
        if arcade.key.A in self.keys_down:
            self.player_facing = "left"
        elif arcade.key.D in self.keys_down:
            self.player_facing = "right"

        # Wenn nicht in Bewegung → keine Animation
        if not moving:
            return

        # Timer
        self.player_anim_timer += delta_time
        if self.player_anim_timer < 0.12:
            return
        self.player_anim_timer = 0

        # Frames auswählen
        frames = self.player_walk_right if self.player_facing == "right" else self.player_walk_left

        # Frame wechseln
        self.player_anim_index = (self.player_anim_index + 1) % len(frames)
        self.Player_sprite.texture = frames[self.player_anim_index]

            
            
            

    def on_key_press(self, symbol, modifiers):
        self.keys_down.add(symbol)
        dx, dy, possible = self.GameMovementEngine.dash_is_possible(symbol, self.keys_down, self.dash_cooldown)
        if dx != 0 or dy != 0: self.dash_x, self.dash_y = dx, dy

        
        for interaction in self.interactiontiles:
            if arcade.check_for_collision(interaction, self.Player_sprite):
                itype = interaction.properties.get("interactiontype")
                if itype == "lobby" and symbol == arcade.key.E:
                    arcade.schedule(lambda dt: self.window.show_view(LobbyView()), 0)

        
        if symbol == arcade.key.ENTER:
            if self.phase < 16:
                self.phase += 1
            else:
                arcade.schedule(lambda dt: self.window.show_view(MenuView(currently_in_game=False)), 0)




    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_down: self.keys_down.remove(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            p = self.camera.unproject((x, y))
            self.GameMovementEngine.player_shoot(p.x, p.y)
