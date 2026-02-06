import arcade
from arcade import gui
import time





class UIEngine():
    def __init__(self, window, Daten):
        self.window = window
        self.all_flashing_cycles = [100, "UP"]
        self.shop_manager = gui.UIManager()
        self.shop_manager.enable()
        self.Daten = Daten
        


        self.text_HP = arcade.Text("", 50, 100, arcade.color.WHITE, 30)
        self.text_Schrott = arcade.Text("", 50, 50, arcade.color.WHITE, 30)
        self.text_level = arcade.Text("", 50, 150, arcade.color.WHITE, 30)
        self.text_ultpoints = arcade.Text("", 50, 200, arcade.color.WHITE, 30)
        
        self.debugtext_TIME = arcade.Text("", self.window.width - 30, self.window.height - 20,
                                          arcade.color.WHITE, 15, anchor_x="right")
        self.debugtext_fps = arcade.Text("", self.window.width - 30, self.window.height - 40,
                                         arcade.color.WHITE, 15, anchor_x="right")
        
        self.dash_sprite = arcade.Sprite("sprites/dash.png")
        self.dash_sprite.center_x = self.window.width // 2
        self.dash_sprite.center_y = 30
        self.dash_sprite.scale = 0.2
        
        # Pre-load shop asset to save memory
        self.miro_sprite = arcade.Sprite("sprites/miro.png")
        self.miro_sprite.scale = 5
        self.miro_sprite.position = (self.window.width, self.window.height)

        self.scrap_sprite = arcade.Sprite("sprites/scrap.png")
        self.scrap_sprite.scale = 0.6

        self.heart_sprite = arcade.Sprite("sprites/heart.png")
        self.heart_sprite.scale = 1.8

        self.text_console = arcade.Text("", 10, 25, arcade.color.BLACK, 15, anchor_x="left", anchor_y="center")
        self.text_console_info = arcade.Text("/command parameter Value", 10, 10, arcade.color.BLACK, 11, anchor_x="left", anchor_y="center")

    def run_cycle(self):
        if self.all_flashing_cycles[1] == "UP":
            self.all_flashing_cycles[0] += 5
            if self.all_flashing_cycles[0] >= 255:
                self.all_flashing_cycles[1] = "DOWN"
        elif self.all_flashing_cycles[1] == "DOWN":
            self.all_flashing_cycles[0] -= 5
            if self.all_flashing_cycles[0] <= 50:
                self.all_flashing_cycles[1] = "UP"
        
    def get_cycle(self):
        return self.all_flashing_cycles[0]
    
    def Game_draw_UI(self, movement_engine, dash_cooldown):
        self.text_HP.draw()
        self.text_Schrott.draw()


        # FIX Step 1: Using the passed engine reference
        current_time = time.monotonic()
        can_dash = (current_time - movement_engine.last_dash_time) >= dash_cooldown
        
        if can_dash:
            self.dash_sprite.alpha = 255
        else:
            self.dash_sprite.alpha = max(0, self.all_flashing_cycles[0] - 50)
            
        arcade.draw_sprite(self.dash_sprite)
        arcade.draw_sprite(self.scrap_sprite, pixelated=True)

        self.heart_sprite.scale = 1.8 + (self.all_flashing_cycles[0] - 50) * (0.4 / (255 - 50))
        arcade.draw_sprite(self.heart_sprite, pixelated=True)
        if hasattr(self, "minimap_sprite_list"):
            self.minimap_sprite_list.draw()
            arcade.draw_lbwh_rectangle_outline(0, self.window.height-self.minimap_height,self.minimap_width,self.minimap_height, arcade.color.WHITE, 2)
    
    def draw_debug(self):
        self.debugtext_TIME.draw()
        self.debugtext_fps.draw()

    def draw_console(self, text):
        arcade.draw_lbwh_rectangle_filled(0, 0, 300, 50, arcade.color.WHITE)
        self.text_console.text = text
        self.text_console.draw()
        self.text_console_info.draw()

    def run_console(self, text, MovementEngine):
        # Entferne führenden Slash, falls vorhanden
        if text.startswith("/"):
            text = text[1:]

        # Teile den Text nach Leerzeichen
        command = text.split(" ")

        # Beispiel: /set health 100 → command = ['set', 'health', '100']
        if command[0] == 'set':
            if command[1] == 'health':
                self.Daten.set_data("Health", int(command[2]))
            elif command[1] == 'scrap':
                self.Daten.set_data("Schrott", int(command[2]))
            elif command[1] == "name":
                # Alles nach dem Befehl als Name zusammenfügen
                name_value = " ".join(command[2:])
                self.Daten.set_data("Username", name_value)
            elif command[1] == "weapon":
                weapon_value = ".".join(command[2:])
                self.Daten.set_data("CurrentWeapon", weapon_value)
            elif command[1] == "level":
                self.Daten.set_data("Levelnumber", int(command[2]))

        elif command[0] == "enemys":
            if command[1] == 'spawn':
                MovementEngine.spawn_enemys()
            elif command[1] == 'kill':
                MovementEngine.kill_all_enemys()

        elif command[0] == "volume":
            if command[1] == 'music':
                self.Daten.set_data("MusicVolume", command[2])
            elif command[1] == 'sound':
                self.Daten.set_data("SoundVolume", command[2])

        elif command[0] == 'overwrite':
            if command[1] == 'damage':
                try:
                    MovementEngine.overwrite_damage = int(command[2])
                except ValueError:
                    if command[2] == "default":
                        MovementEngine.overwrite_damage = None
            elif command[1] == 'speed':
                try:
                    MovementEngine.overwrite_playerspeed = int(command[2])
                except ValueError:
                    if command[2] == "default":
                        MovementEngine.overwrite_playerspeed = None



    def update_minimap(self, tilemap, scene, player, path_enemys, follow_enemys, interactiontiles):
        
        map_width  = tilemap.width * tilemap.tile_width * tilemap.scaling
        map_height = tilemap.height * tilemap.tile_height * tilemap.scaling

        self.enemy_dot = arcade.make_circle_texture(12, arcade.color.RED)

        proj = (0, map_width, 0, map_height)

        atlas = self.minimap_sprite_list.atlas

        with atlas.render_into(self.minimap_texture, projection=proj) as fbo:
            fbo.clear(color=arcade.color.BLACK)

            scene.draw()

            arcade.draw_circle_filled(player.center_x, player.center_y, 50, arcade.color.PURPLE)

            for enemy in path_enemys:
                arcade.draw_circle_filled(enemy.center_x, enemy.center_y, 25, arcade.color.RED)
            
            for enemy in follow_enemys:
                arcade.draw_circle_filled(enemy.center_x, enemy.center_y, 25, arcade.color.BLUE)
            
            for interaction in interactiontiles:
                arcade.draw_lbwh_rectangle_filled(interaction.center_x-interaction.width//2,interaction.center_y-interaction.height//2,interaction.width, interaction.height, arcade.color.GREEN)

    def minimap_setup(self):
        # --- Minimap Setup ---
        self.minimap_width = 256
        self.minimap_height = 256

        # Leere Texture erzeugen
        self.minimap_texture = arcade.Texture.create_empty(
            "minimap",
            (self.minimap_width, self.minimap_height)
        )

        # Sprite, das die Minimap anzeigt
        self.minimap_sprite = arcade.Sprite(
            self.minimap_texture,
            center_x=self.minimap_width // 2,
            center_y=self.window.height - self.minimap_height // 2
        )

        self.minimap_sprite_list = arcade.SpriteList()
        self.minimap_sprite_list.append(self.minimap_sprite)

    def Game_draw_enemy_health(self, Movementengine):

        def health_to_color(health):
                if health >= 80:
                    return arcade.color.GREEN
                elif health >= 60:
                    return arcade.color.YELLOW
                elif health >= 40:
                    return arcade.color.ORANGE
                else:
                    return arcade.color.RED

        PathEnemyList, FollowEnemyList, RetourningList = Movementengine.get_all_enemy_lists()
        for enemy in PathEnemyList:
            health_in_prozent = (enemy.health/enemy.abs_health)*100

            arcade.draw_lbwh_rectangle_filled(enemy.center_x - 50, enemy.center_y + 50, health_in_prozent, 5, health_to_color(health_in_prozent))


        for enemy in FollowEnemyList:
            health_in_prozent = (enemy.health/enemy.abs_health)*100
            arcade.draw_lbwh_rectangle_filled(enemy.center_x - 50, enemy.center_y + 50, health_in_prozent, 5, health_to_color(health_in_prozent))


        for enemy in RetourningList:
            health_in_prozent = (enemy.health/enemy.abs_health)*100
            arcade.draw_lbwh_rectangle_filled(enemy.center_x - 50, enemy.center_y + 50, health_in_prozent, 5, health_to_color(health_in_prozent))

    def Game_update_UI(self):
        
        self.text_HP.text = f"HP: {self.Daten.get_one_data('Health')}"
        self.text_Schrott.text = f"Schrott: {int(self.Daten.get_one_data('Schrott'))}"
        if hasattr(self, "minimap_sprite_list"):
            self.text_HP.position = (42, self.window.height - self.minimap_height - 42)
            self.text_Schrott.position = (42, self.window.height - self.minimap_height - 84)
        else:
            self.text_HP.position = (50, 100)
            self.text_Schrott.position = (50, 50)
        

        self.text_ultpoints.text = f"Ultpoints: {self.Daten.get_one_data('Ultpoints')}"
        self.text_level.text = f"Level: {self.Daten.get_one_data('Levelnumber')}"
        
        self.debugtext_TIME.text = f"{time.monotonic():.2f}"
        self.debugtext_fps.text = f"FPS: {round(arcade.get_fps(60),1)}"
        self.scrap_sprite.center_x = self.text_Schrott.position[0] - 15
        self.scrap_sprite.center_y = self.text_Schrott.position[1] + 10
        self.heart_sprite.center_x = self.text_HP.position[0] - 15
        self.heart_sprite.center_y = self.text_HP.position[1] + 10

    def shop(self):
        self.shop_init()
        # Panels zeichnen
        arcade.draw_lbwh_rectangle_filled(self.left_x, self.left_y, self.left_w, self.left_h, arcade.color.WHITE_SMOKE)
        arcade.draw_lbwh_rectangle_filled(self.right_x, self.right_y, self.right_w, self.right_h, arcade.color.WHITE_SMOKE)
        # Buttons zeichnen
        self.shop_manager.draw()
        self.shop_weapon_text_name.draw()
        self.shop_weapon_text_info.draw()
        self.shop_weapon_text_speed.draw()
        self.shop_weapon_text_damage.draw()
        self.shop_weapon_text_cost.draw()
        arcade.draw_sprite(self.scrap_sprite, pixelated=True)
        arcade.draw_sprite(self.weapon_sprite)

    def shop_init(self):
        # Shop Buttons
        self.left_button = gui.UIFlatButton(text="Waffe verbessern", width=200, height=60)
        self.right_button = gui.UIFlatButton(text="Ult verbessern", width=200, height=60)
        self.sound_weapon_upgrade = arcade.Sound("sounds/levelup.wav")
        
        

        # Klick-Events
        @self.left_button.event("on_click")
        def on_left_click(event):
            if self.Daten.get_one_data("Schrott") > NextWeaponInfos["cost"]:
                self.Daten.upgrade_weapon()
                arcade.play_sound(self.sound_weapon_upgrade, volume=int(self.Daten.get_one_data("SoundVolume")), loop=False)


        @self.right_button.event("on_click")
        def on_right_click(event):
            pass

        # Buttons zum Manager hinzufügen
        self.shop_manager.add(self.left_button)
        self.shop_manager.add(self.right_button)
        
        shop_left = 100
        shop_bottom = 100
        shop_width = self.window.width - 200
        shop_height = self.window.height - 200
        self.complete_height = shop_bottom + shop_height

          # Panels berechnen
        self.left_x = shop_left + 50
        self.left_y = shop_bottom + 50
        self.left_w = shop_width // 2 - 100
        self.left_h = shop_height - 100
        

        self.right_x = shop_left + shop_width - self.left_w - 50
        self.right_y = shop_bottom + 50
        self.right_w = self.left_w
        self.right_h = self.left_h

        self.panelwidth = self.right_w
        

        self.left_button.center_x = self.left_x + self.left_w // 2
        self.left_button.center_y = self.left_y + 40


        self.right_button.center_x = self.right_x + self.right_w // 2
        self.right_button.center_y = self.right_y + 40

        self.left_panel_middle = self.left_button.center_x #(self.left_x + self.left_w)

        # BACKGROUND
        arcade.draw_lbwh_rectangle_filled(
        shop_left,
        shop_bottom,
        shop_width,
        shop_height,
        arcade.color.WHITE)

        CurrentWeapon = self.Daten.get_one_data("CurrentWeapon")
        CurrentLevel = int(CurrentWeapon[-1])
        if CurrentLevel < 3:
            NextWeapon = f"{CurrentWeapon[0]}.{CurrentLevel + 1}"
        else:
            NextWeapon = f"{int(CurrentWeapon[0]) + 1}.1"

        NextWeaponInfos = self.Daten.get_all_weapon_data(NextWeapon)
        CurrentWeaponInfos = self.Daten.get_all_weapon_data(CurrentWeapon)


        
        self.weapon_sprite = arcade.Sprite(f"sprites/weapons/{self.Daten.get_one_weapon_data(NextWeapon, "sprite")}")
        self.weapon_sprite.scale = 0.5
        self.weapon_sprite.center_x = self.left_panel_middle
        self.weapon_sprite.center_y = self.complete_height // 2 + 100

        
        # NAME
        self.shop_weapon_text_name = arcade.Text(
            NextWeaponInfos["name"],
            x=self.left_panel_middle,
            y=self.complete_height-100,
            color=arcade.color.BLACK, font_size=30, width=450, multiline=True, anchor_x="center", anchor_y="center", align="center")

        # INFO
        self.shop_weapon_text_info = arcade.Text(
            NextWeaponInfos["info"],
            x=self.left_panel_middle,
            y=self.complete_height-150,
            color=arcade.color.BLACK, font_size=20, width=450, multiline=True, anchor_x="center", anchor_y="center", align="center")

        self.shop_weapon_text_speed = arcade.Text(
            f"Schussgeschwindigkeit: {round(1/CurrentWeaponInfos["speed"],1)} -> {round(1/NextWeaponInfos["speed"],1)}",
            x=self.left_panel_middle,
            y=self.left_button.center_y + 100,
            color=arcade.color.BLACK, font_size=20, width=450, multiline=True, anchor_x="center", anchor_y="center", align="center")

        self.shop_weapon_text_damage = arcade.Text(
            f"Schaden: {CurrentWeaponInfos["damage"]} -> {NextWeaponInfos["damage"]}",
            x=self.left_panel_middle,
            y=self.left_button.center_y + 125,
            color=arcade.color.BLACK, font_size=20, width=450, multiline=True, anchor_x="center", anchor_y="center", align="center")
        
        self.shop_weapon_text_cost = arcade.Text(
            f"{NextWeaponInfos["cost"]}",
            x=self.left_panel_middle - 20,
            y=self.left_button.center_y + 50,
            color=arcade.color.BLACK, font_size=20, width=450, multiline=True, anchor_x="center", anchor_y="center", align="center")
        
        self.scrap_sprite.center_x = self.left_panel_middle + 20
        self.scrap_sprite.center_y = self.left_button.center_y + 50