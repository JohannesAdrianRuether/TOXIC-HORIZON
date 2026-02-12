import arcade
import random
from MovementEngine import * 
from UIEngine import *
import Data
from path_utils import asset_path

class LoadingScreen(arcade.View):
    def __init__(self):
        super().__init__()
        self.loading_in_prozent = 0

    def on_draw(self):
        self.clear()
        print(self.loading_in_prozent)

    def load_GameView(self):
        self.daten_setup_GameView()
        self.loading_in_prozent += 20
        self.scene_setup_GameView()
        self.loading_in_prozent += 20
        self.sprite_setup_GameView()
        self.loading_in_prozent += 20
        self.movement_setup_GameView()
        self.loading_in_prozent += 20
        self.ui_setup_GameView()
        self.loading_in_prozent += 20
        return self


    def scene_setup_GameView(self):
        map_pfad = random.choice(self.map_list)
        self.tilemap = arcade.load_tilemap(map_pfad, scaling=2, layer_options={"Walls": {"use_spatial_hash": True}})
        self.scene = arcade.Scene.from_tilemap(self.tilemap)

    def daten_setup_GameView(self):
        self.Daten = Data.DatenManagement()
        self.map_list = self.Daten.get_one_data("Maplist")
        self.Daten.autosave()

    def sprite_setup_GameView(self):
        self.window.set_mouse_visible(False)
        self.crosshair = arcade.Sprite(asset_path("assets/sprites/crosshair.png"))
        self.Player_sprite = arcade.Sprite()
        self.Player_sprite.scale = 0.5
        self.player_walk_right = [
            arcade.load_texture(asset_path("assets/sprites/player/walk_right_1.png")),
            arcade.load_texture(asset_path("assets/sprites/player/walk_right_2.png")),
            arcade.load_texture(asset_path("assets/sprites/player/walk_right_3.png")),
        ]

        self.player_walk_left = [
            arcade.load_texture(asset_path("assets/sprites/player/walk_left_1.png")),
            arcade.load_texture(asset_path("assets/sprites/player/walk_left_2.png")),
            arcade.load_texture(asset_path("assets/sprites/player/walk_left_3.png")),
        ]
        self.button_e_sprite = arcade.Sprite(asset_path("assets/sprites/EButton.png"))

        self.player_anim_timer = 0
        self.player_anim_index = 0
        self.player_facing = "right"

        # Starttexture
        self.Player_sprite.texture = self.player_walk_right[0]

    def movement_setup_GameView(self):
        self.camera = arcade.Camera2D()
        self.GameMovementEngine = MovementEngine(self.scene, self.camera, self.window, self.Daten)
        for spawn in self.scene["spawns"]:
            if spawn.properties.get("spawn") == "player":
                self.Player_sprite.center_x, self.Player_sprite.center_y = spawn.center_x, spawn.center_y
        self.dash_x, self.dash_y = 0, 0
        self.dash_decay, self.dash_cooldown = 1.2, 1.5
        self.keys_down = set()
        self.Daten.set_data("Health", 100)
        self.GameMovementEngine.spawn_enemys()
        self.playerisdead = False

    def ui_setup_GameView(self):
        self.gui_camera = arcade.Camera2D()
        self.GameUIEngine = UIEngine(self.window, self.Daten)
        self.GameUIEngine.minimap_setup()
        self.text_username = arcade.Text(self.Daten.get_one_data("Username"), 0, 0, arcade.color.WHITE, 15, anchor_x="center")
        self.sound_music = arcade.Sound(asset_path("assets/sounds/gamemusic.mp3"))
        #arcade.play_sound(self.sound_music, loop=True, volume=int(Daten.get_one_data("MusicVolume")))
        self.interactiontiles = self.scene["interactions"]
        self.show_console = False
        self.consoletext = ''

