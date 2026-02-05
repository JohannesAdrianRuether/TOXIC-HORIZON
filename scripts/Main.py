import arcade
import tkinter as tk
from tkinter import messagebox
import arcade.gui as gui
import webbrowser
from MovementEngine import * 
from UIEngine import *
import Tutorial
import Data
global Daten
Daten = Data.DatenManagement()

monitor = arcade.get_display_size()
SCREEN_WIDTH = monitor[0]
SCREEN_HEIGHT = monitor[1]


class MenuView(arcade.View):
    def __init__(self, currently_in_game):
        super().__init__()
        self.loading_success = currently_in_game
        self.manager = gui.UIManager()
        self.background_color = arcade.color.BLACK
        
        v_box = gui.UIBoxLayout(space_between=20)
        if currently_in_game == False:
            start_btn = gui.UIFlatButton(text="START", width=200)
        else:
            start_btn = gui.UIFlatButton(text="WEITER", width=200)
        new_btn = gui.UIFlatButton(text="NEU", width=200)
        load_btn = gui.UIFlatButton(text="LADEN", width=200)
        save_btn = gui.UIFlatButton(text="SPEICHERN", width=200)
        tut_btn = gui.UIFlatButton(text="TUTORIAL", width=200)
        help_btn = gui.UIFlatButton(text="MIRI'S WIKI ", width=200)
        exit_btn = gui.UIFlatButton(text="EXIT", width=200)

        @start_btn.event('on_click')
        def on_click_start(event):
            if self.loading_success:
                arcade.schedule(lambda dt: self.window.show_view(LobbyView()), 0)
        @new_btn.event('on_click')
        def on_click_new(event):
            arcade.schedule(lambda dt: self.window.show_view(NewGameView()), 0)
        @load_btn.event('on_click')
        def on_click_load(event):
            self.window.set_visible(False)
            self.loading_success = Daten.laden()
            self.window.set_visible(True)
        @tut_btn.event('on_click')
        def on_click_exit(event):
            arcade.schedule(lambda dt: self.window.show_view(Tutorial.Tutorial()), 0)
        @exit_btn.event('on_click')
        def on_click_exit(event):
            arcade.close_window()
        @help_btn.event('on_click')
        def on_click_exit(event):
            webbrowser.open("miris_wiki.html")
        @save_btn.event('on_click')
        def on_click_exit(event):
            self.window.set_visible(False)
            Daten.speichern()
            self.window.set_visible(True)
        v_box.add(start_btn)
        v_box.add(new_btn)
        v_box.add(load_btn)
        v_box.add(save_btn)
        v_box.add(tut_btn)
        v_box.add(help_btn)
        v_box.add(exit_btn)
        

        anchor = gui.UIAnchorLayout()
        anchor.add(
            child=v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor)

        
    def on_show_view(self):
        self.manager.enable()
    def on_hide_view(self):
        self.manager.disable()
    def on_draw(self):
        self.clear()
        
        self.manager.draw()
        

class NewGameView(arcade.View):
    def __init__(self):
        super().__init__()
        self._username = ""
        self.text_title = arcade.Text("Benennen Sie Ihren Charakter", self.window.width // 2, self.window.height // 2 + 300, arcade.color.WHITE, 30, anchor_x="center")
        self.Player_sprite = arcade.Sprite("sprites/player/walk_right_1.png")
        self.Player_sprite.scale = 4

    def on_draw(self):
        self.clear()
        self.text_title.draw()
        arcade.Text(self._username, self.window.width // 2, self.window.height // 2 + 250, arcade.color.WHITE, 25, anchor_x="center").draw()
        self.Player_sprite.center_x, self.Player_sprite.center_y = self.window.width // 2, self.window.height // 2
        arcade.draw_sprite(self.Player_sprite, pixelated=True)

    def on_text(self, text):
        if text.isprintable() and len(self._username) < 20: self._username += text
    def on_key_press(self, key, modifiers):
        if key == arcade.key.BACKSPACE: self._username = self._username[:-1]
        elif key == arcade.key.ENTER:
            Daten.set_data("Username", self._username)
            Daten.set_data("Health", 100)
            Daten.autosave()
            arcade.schedule(lambda dt: self.window.show_view(LobbyView()), 0)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        Daten.autosave()
        map_pfad = "maps/Map1.tmx"
        self.window.set_mouse_visible(False)
        self.crosshair = arcade.Sprite("sprites/crosshair.png")
        self.sound_music = arcade.Sound("sounds/gamemusic.mp3")
        arcade.play_sound(self.sound_music, loop=True, volume=0.25)

        self.tilemap = arcade.load_tilemap(map_pfad, scaling=2, layer_options={"Walls": {"use_spatial_hash": True}})

        
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.Player_sprite = arcade.Sprite()
        self.Player_sprite.scale = 2

        self.player_walk_right = [
            arcade.load_texture("sprites/player/walk_right_1.png"),
            arcade.load_texture("sprites/player/walk_right_1.png"),
            arcade.load_texture("sprites/player/walk_right_1.png"),
        ]

        self.player_walk_left = [
            arcade.load_texture("sprites/player/walk_left_1.png"),
            arcade.load_texture("sprites/player/walk_left_1.png"),
            arcade.load_texture("sprites/player/walk_left_1.png"),
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
        self.button_e_sprite = arcade.Sprite("sprites/EButton.png")
        Daten.set_data("Health", 100)
        self.GameUIEngine.minimap_setup()



    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()

        self.GameUIEngine.Game_draw_enemy_health(self.GameMovementEngine)

        
        self.text_username.draw()
        for interaction in self.interactiontiles:
            if arcade.check_for_collision(interaction, self.Player_sprite):
                interactiontype = interaction.properties.get("interactiontype", None)
                if interactiontype in ["lobby"]:
                    self.button_e_sprite.center_x = self.Player_sprite.center_x
                    self.button_e_sprite.center_y = self.Player_sprite.center_y - 60
                    self.button_e_sprite.alpha = self.GameUIEngine.get_cycle()
                    arcade.draw_sprite(self.button_e_sprite)

        self.GameMovementEngine.draw_enemys()
        arcade.draw_sprite(self.Player_sprite, pixelated=True)
        self.gui_camera.use()

        arcade.draw_sprite(self.crosshair, pixelated=True)

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
        self.GameMovementEngine.run_enemy_movement(self.Player_sprite)
        self.playerisdead = self.GameMovementEngine.all_collision_checks(self.Player_sprite)
        self.GameUIEngine.update_minimap(self.tilemap, self.scene, self.Player_sprite, self.GameMovementEngine.path_Enemy_sprite_list, self.GameMovementEngine.following_Enemy_sprite_list, self.interactiontiles)
        

        self.dash_x, self.dash_y = self.GameMovementEngine.player_movement(
            self.Player_sprite, self.keys_down,
            self.dash_x, self.dash_y, self.dash_decay, delta_time
        )

        self.text_username.x = self.Player_sprite.center_x
        self.text_username.y = self.Player_sprite.center_y + 55
        self.update_player_animation(delta_time)
        


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




    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_down: self.keys_down.remove(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            p = self.camera.unproject((x, y))
            self.GameMovementEngine.player_shoot(p.x, p.y)

    def on_mouse_motion(self, x, y, dx, dy):
        self.crosshair.position = (x,y)

class LobbyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.tilemap = arcade.load_tilemap("maps/LobbyMap.tmx", scaling=2, layer_options={"Walls": {"use_spatial_hash": True}})
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.Player_sprite = arcade.Sprite()
        self.Player_sprite.scale = 2

        # Walk only
        self.player_walk_right = [
            arcade.load_texture("sprites/player/walk_right_1.png"),
            arcade.load_texture("sprites/player/walk_right_1.png"),
            arcade.load_texture("sprites/player/walk_right_1.png"),
        ]

        self.player_walk_left = [
            arcade.load_texture("sprites/player/walk_left_1.png"),
            arcade.load_texture("sprites/player/walk_left_1.png"),
            arcade.load_texture("sprites/player/walk_left_1.png"),
        ]

        self.player_anim_timer = 0
        self.player_anim_index = 0
        self.player_facing = "right"

        # Starttexture
        self.Player_sprite.texture = self.player_walk_right[0]


        self.button_e_sprite = arcade.Sprite("sprites/EButton.png")

        for spawn in self.scene["spawns"]:
            if spawn.properties.get("spawn") == "player":
                self.Player_sprite.center_x, self.Player_sprite.center_y = spawn.center_x, spawn.center_y

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.LobbyMovementEngine = MovementEngine(self.scene, self.camera, self.window, Daten)
        self.LobbyUIEngine = UIEngine(self.window, Daten)
        self.keys_down = set()
        self.dash_x, self.dash_y = 0, 0
        self.dash_decay, self.dash_cooldown = 1.2, 1.2
        self.shop_is_entered = False
        self.interactiontiles = self.scene["interactions"]
        self.text_username = arcade.Text(Daten.get_one_data("Username"), 0, 0, arcade.color.WHITE, 15, anchor_x="center")

    def on_show_view(self):
        Daten.autosave()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        arcade.draw_sprite(self.Player_sprite, pixelated=True)
        self.text_username.draw()

        for interaction in self.interactiontiles:
            if arcade.check_for_collision(interaction, self.Player_sprite):
                interactiontype = interaction.properties.get("interactiontype", None)
                if interactiontype in ["shop", "startgame"]:
                    self.button_e_sprite.center_x = self.Player_sprite.center_x
                    self.button_e_sprite.center_y = self.Player_sprite.center_y - 60
                    self.button_e_sprite.alpha = self.LobbyUIEngine.get_cycle()
                    arcade.draw_sprite(self.button_e_sprite)

        self.gui_camera.use()
        if self.shop_is_entered:
            self.LobbyUIEngine.shop()
        else:
            self.LobbyUIEngine.Game_draw_UI(self.LobbyMovementEngine, self.dash_cooldown)

        if arcade.key.F3 in self.keys_down:
            self.LobbyUIEngine.draw_debug()

    def on_update(self, delta_time):
        self.dash_x, self.dash_y = self.LobbyMovementEngine.player_movement(self.Player_sprite, self.keys_down, self.dash_x, self.dash_y, self.dash_decay, delta_time)
        self.LobbyUIEngine.run_cycle()
        self.LobbyUIEngine.Game_update_UI()
        self.text_username.x, self.text_username.y = self.Player_sprite.center_x, self.Player_sprite.center_y + 55
        self.update_player_animation(delta_time)
        
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
        dx, dy, possible = self.LobbyMovementEngine.dash_is_possible(symbol, self.keys_down, self.dash_cooldown)
        if dx != 0 or dy != 0: self.dash_x, self.dash_y = dx, dy
        
        for interaction in self.interactiontiles:
            if arcade.check_for_collision(interaction, self.Player_sprite):
                itype = interaction.properties.get("interactiontype")
                if itype == "shop" and symbol == arcade.key.E:
                    self.shop_is_entered = True
                elif itype == "startgame" and symbol == arcade.key.E:
                    arcade.schedule(lambda dt: Daten.change_data("Levelnumber", 1), 0)
                    arcade.schedule(lambda dt: self.window.show_view(GameView()), 0)

        if symbol == arcade.key.ESCAPE and self.shop_is_entered == True:
            self.shop_is_entered = False

        if symbol == arcade.key.ESCAPE and self.shop_is_entered == False:
            arcade.schedule(lambda dt: self.window.show_view(MenuView(currently_in_game = True)), 0)


    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_down: self.keys_down.remove(symbol)

class GameOver(arcade.View):
    def __init__(self):
        super().__init__()
        self.loading_success = False
        self.manager = gui.UIManager()
        self.text_dead = arcade.Text("Werden gestorben haben.", self.window.width//2, self.window.height//1.5, arcade.color.WHITE, 42, anchor_x="center")
        self.text_level = arcade.Text(f"Level: {Daten.get_one_data("Levelnumber")}", self.window.width//2, self.window.height//1.6, arcade.color.WHITE, 20, anchor_x="center")
        
        # UI Buttons (Simplified for readability)
        v_box = gui.UIBoxLayout(space_between=20)
        new_btn = gui.UIFlatButton(text="NEU", width=200)
        again_btn = gui.UIFlatButton(text="ERNEUT (-1/3 Schrott)", width=200)
        exit_btn = gui.UIFlatButton(text="EXIT", width=200)
        @new_btn.event('on_click')
        def on_click_new(event):
            arcade.schedule(lambda dt: self.window.show_view(NewGameView()), 0)
        @again_btn.event('on_click')
        def on_click_new(event):
            Schrott = Daten.get_one_data('Schrott')
            NewSchrott = Schrott * 0.66
            Daten.set_data('Schrott', NewSchrott)

            arcade.schedule(lambda dt: self.window.show_view(LobbyView()), 0)
        @exit_btn.event('on_click')
        def on_click_exit(event):
            arcade.close_window()


        v_box.add(new_btn)
        v_box.add(again_btn)
        v_box.add(exit_btn)

        anchor = gui.UIAnchorLayout()
        anchor.add(
            child=v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor)

        
    def on_show_view(self):
        self.manager.enable()
    def on_hide_view(self):
        self.manager.disable()
    def on_draw(self):
        self.clear()
        self.text_dead.draw()
        self.text_level.draw()
        self.manager.draw()


class StartUp(arcade.View):
    def __init__(self):
        super().__init__()
        self.woosh = arcade.Sound("sounds/woosh.ogg")
        self.background_color = arcade.color.BLACK
        self.text_studio = arcade.Text("INSTINCT√9", self.window.width//2, self.window.height//2, arcade.color.WHITE, 124, anchor_x="center", anchor_y="center", bold=True, font_name="Liberation Mono")
        self.sprite_background = arcade.Sprite("sprites/LOGO.png")
        self.sprite_background.position = (self.window.width//2, self.window.height//2.25)
        self.sprite_background.scale = 2
        self.start = time.monotonic()
        arcade.play_sound(self.woosh, 3, speed=0.5)

    def on_draw(self):
        self.clear()
        self.text_studio.draw()
        if time.monotonic() - self.start >= 4:
            arcade.draw_sprite(self.sprite_background)
        if time.monotonic() - self.start >= 8:
            self.window.show_view(MenuView(currently_in_game = False))
   
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.SPACE:
            self.window.show_view(GameView())

def main():
    arcade.enable_timings()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "TOXIC HORIZON", fullscreen=True)
    window.show_view(StartUp())
    arcade.run()

if __name__ == "__main__":
    main()

