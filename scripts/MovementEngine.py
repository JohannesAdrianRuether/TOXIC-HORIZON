import arcade, time, random, math
from path_utils import asset_path

class MovementEngine():
    """Handles player movement, enemy logic, bullets, collision checks, and drops."""
    def __init__(self, scene, camera, window, Daten):
        """Store world references and initialize combat/movement runtime state."""
        self.scene = scene
        self.camera = camera
        self.last_dash_time = 0
        self.last_shoot_time = 0
        self.bullet_sprite_list = arcade.SpriteList()
        self.window = window
        self.scrap_list = arcade.SpriteList()
        self.Daten = Daten
        self.abandon_path_list = arcade.SpriteList()
        self.retourning_list = arcade.SpriteList()
        self.player_is_dead = False
        self.sound_shot = arcade.Sound(asset_path("assets/sounds/singleshot.mp3"))
        self.sound_walk = arcade.Sound(asset_path("assets/sounds/walk.mp3"))
        self.walk_handle = None
        self.overwrite_damage = None
        self.overwrite_playerspeed = None


    def player_movement(self, player, keys_down, dash_x, dash_y, dash_decay, delta_time):
        """Apply WASD movement + dash movement + walk sound state machine."""
        self.player = player
        if self.overwrite_playerspeed == None:
            speed = 300 * delta_time
        else:
            speed = self.overwrite_playerspeed * delta_time
        walls = self.scene["Walls"]
        

        self.camera.position = self.player.position

        move_x = 0
        move_y = 0

        if arcade.key.W in keys_down: move_y += 1
        if arcade.key.S in keys_down: move_y -= 1
        if arcade.key.A in keys_down: move_x -= 1
        if arcade.key.D in keys_down: move_x += 1

        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        final_x = move_x * speed
        final_y = move_y * speed

        self.player.center_x += final_x
        if arcade.check_for_collision_with_list(self.player, walls):
            self.player.center_x -= final_x

        self.player.center_y += final_y
        if arcade.check_for_collision_with_list(self.player, walls):
            self.player.center_y -= final_y

        # Prüfen, ob eine Bewegungstaste gedrückt wird
        is_moving = move_x != 0 or move_y != 0

        if is_moving:
            # Wenn der Sound noch nicht spielt, starte ihn
            if self.walk_handle is None:
                self.walk_handle = arcade.play_sound(self.sound_walk, loop=True, volume=int(self.Daten.get_one_data("SoundVolume")), speed=20)
        else:
            # Wenn der Spieler steht, aber der Sound noch läuft: Stoppen!
            if self.walk_handle is not None:
                arcade.stop_sound(self.walk_handle)
                self.walk_handle = None
        # Dash Movement
        self.player.center_x += dash_x
        self.player.center_y += dash_y
        if arcade.check_for_collision_with_list(self.player, walls):
            self.player.center_x -= dash_x
            self.player.center_y -= dash_y
            dash_x = 0
            dash_y = 0

        dash_x /= dash_decay
        dash_y /= dash_decay

        if abs(dash_x) < 0.5: dash_x = 0
        if abs(dash_y) < 0.5: dash_y = 0

        return dash_x, dash_y
    
    def dash_is_possible(self, symbol, keys_down, dash_cooldown):
        """Validate dash cooldown and return dash impulse vector if available."""
        current_time = time.monotonic()
        can_dash = (current_time - self.last_dash_time) >= dash_cooldown

        if symbol != arcade.key.SPACE or not can_dash:
            return 0, 0, can_dash

        dash_speed = 20
        dash_x = 0
        dash_y = 0

        if arcade.key.W in keys_down: dash_y = dash_speed
        if arcade.key.S in keys_down: dash_y = -dash_speed
        if arcade.key.A in keys_down: dash_x = -dash_speed
        if arcade.key.D in keys_down: dash_x = dash_speed

        if dash_x == 0 and dash_y == 0:
            return 0, 0, True

        self.last_dash_time = current_time
        return dash_x, dash_y, False

    def spawn_enemys(self):
        """Spawn both follower and path enemies from map spawn markers."""
        if self.scene['spawns'] != None:
            self.following_Enemy_sprite_list = arcade.SpriteList()
            self.follow_enemy_speed = 4
            self.path_Enemy_sprite_list = arcade.SpriteList()
            self.path_enemy_speed = 5

            spawner = self.scene["spawns"]
            FollowEnemySpawner = [s for s in spawner if s.properties.get("spawn") == 'enemy1']
            PathEnemySpawnerONE = [s for s in spawner if s.properties.get("spawn") == 'enemy2']

            for i in range(len(FollowEnemySpawner)):
                enemy = arcade.Sprite()
                enemy.scale = 3

                # --- TEXTURES EINMAL LADEN ---
                enemy.textures = [
                    arcade.load_texture(asset_path("assets/sprites/enemy2/Drone1.png")),
                    arcade.load_texture(asset_path("assets/sprites/enemy2/Drone2.png"))
                ]

                enemy.current_texture = 0
                enemy.texture = enemy.textures[0]
                enemy.animation_timer = 0.0

                enemy.health = 20 + self.Daten.get_one_data("Levelnumber") * 2 + self.Daten.get_one_data("Levelnumber")**1.2
                enemy.abs_health = enemy.health

                enemy.origin_is_follow = True

                enemy.change_x = 0
                enemy.change_y = 0

                self.following_Enemy_sprite_list.append(enemy)


            for i in range(len(PathEnemySpawnerONE)):
                enemy = arcade.Sprite()
                enemy.scale = 2

                # --- TEXTURES EINMAL LADEN ---
                enemy.textures = [
                    arcade.load_texture(asset_path("assets/sprites/spider/spider1.png")),
                    arcade.load_texture(asset_path("assets/sprites/spider/spider2.png")),
                    arcade.load_texture(asset_path("assets/sprites/spider/spider3.png")),
                    arcade.load_texture(asset_path("assets/sprites/spider/spider4.png")),
                ]

                enemy.current_texture = 0
                enemy.texture = enemy.textures[0]
                enemy.animation_timer = 0.0

                enemy.health = 25 + self.Daten.get_one_data("Levelnumber") * 2 + self.Daten.get_one_data("Levelnumber") ** 1.2
                enemy.abs_health = enemy.health

                enemy.change_x = 0
                enemy.change_y = 0
                enemy.is_path = True

                self.path_Enemy_sprite_list.append(enemy)
            
            

            for enemy in self.following_Enemy_sprite_list:
                spawn = FollowEnemySpawner.pop()
                enemy.center_x, enemy.center_y = spawn.center_x, spawn.center_y

            for enemy in self.path_Enemy_sprite_list:
                spawn = PathEnemySpawnerONE.pop()
                enemy.center_x, enemy.center_y = spawn.center_x, spawn.center_y

    def draw_enemys(self):
        """Draw enemy lists, active bullets, scrap drops, and returning enemies."""
        self.following_Enemy_sprite_list.draw(pixelated=True)
        self.path_Enemy_sprite_list.draw(pixelated=True)
        self.bullet_sprite_list.draw(pixelated=True)
        self.scrap_list.draw(pixelated=True)
        self.retourning_list.draw(pixelated=True)

    def _direction_to_vector(self, direction):
        """Convert symbolic direction to unit vector used by path logic."""
        # Helper: direction string -> (vx, vy)
        if direction == "left": return -1, 0
        if direction == "right": return 1, 0
        if direction == "up": return 0, 1
        if direction == "down": return 0, -1
        return 0, 0

    def run_enemy_movement(self, player):
        """Advance follower/path/returning enemy behavior and projectile motion."""
        walls = self.scene["Walls"]
        paths = self.scene["enemypath"]
        aggro = 1
        # 1) Followers (unchanged simple chase)
        for enemy in self.following_Enemy_sprite_list:
            if (enemy.health/enemy.abs_health)*100 < 25:
                aggro = 1.5
            dx, dy = player.center_x - enemy.center_x, player.center_y - enemy.center_y
            d = math.hypot(dx, dy)
            if d > 5:
                enemy.change_x = (dx / d) * self.follow_enemy_speed * aggro
                enemy.change_y = (dy / d) * self.follow_enemy_speed * aggro

                enemy.center_x += enemy.change_x
                if not hasattr(enemy, "origin_is_follow"):
                    if arcade.check_for_collision_with_list(enemy, walls):
                        enemy.center_x -= enemy.change_x

                enemy.center_y += enemy.change_y
                if not hasattr(enemy, "origin_is_follow"):
                    if arcade.check_for_collision_with_list(enemy, walls):
                        enemy.center_y -= enemy.change_y

            self.update_enemy_rotation(enemy)
            self.update_enemy_animation(enemy, self.window.delta_time)

        # 2) PATH ENEMIES (patrouille) - wie vorher (keine Änderung nötig)
        for enemy in list(self.path_Enemy_sprite_list):
            if (enemy.health/enemy.abs_health)*100 < 25:
                aggro = 1.5
            hit_list = arcade.check_for_collision_with_list(enemy, paths)
            path_x, path_y = enemy.change_x, enemy.change_y
            for tile in hit_list:
                if math.hypot(enemy.center_x - tile.center_x, enemy.center_y - tile.center_y) < 4:
                    direction = tile.properties.get("direction", None)
                    if direction == "left": path_x, path_y = -1, 0
                    elif direction == "right": path_x, path_y = 1, 0
                    elif direction == "up": path_x, path_y = 0, 1
                    elif direction == "down": path_x, path_y = 0, -1
            enemy.center_x += path_x * self.path_enemy_speed  * aggro
            enemy.center_y += path_y * self.path_enemy_speed * aggro
            enemy.change_x, enemy.change_y = path_x, path_y

            # Aggro -> Wechsel in following (wie gehabt)
            dist_to_player = math.hypot(player.center_x - enemy.center_x, player.center_y - enemy.center_y)
            if dist_to_player < 200:
                try:
                    self.path_Enemy_sprite_list.remove(enemy)
                except ValueError:
                    pass
                if enemy not in self.following_Enemy_sprite_list:
                    self.following_Enemy_sprite_list.append(enemy)
            self.update_enemy_rotation(enemy)
            self.update_enemy_animation(enemy, self.window.delta_time)


        # 3) NEAREST-TILE CHECK während Verfolgung (NEU)
        # Für jeden Gegner, der ursprünglich ein Path-Enemy war, prüfe fortlaufend die nächste Path-Tile.
        for enemy in list(self.following_Enemy_sprite_list):
            if getattr(enemy, "is_path", False) and len(paths) > 0:
                # arcade.get_closest_sprite liefert (sprite, dist) oder None
                closest = arcade.get_closest_sprite(enemy, paths)
                if closest is not None:
                    tile, dist = closest
                    # Wenn die Distanz zum nächsten Pfad-Tile größer als 100 ist -> zurücklaufen
                    if dist > 400:
                        # Ziel speichern und in retourning_list verschieben
                        enemy.return_target_x = tile.center_x
                        enemy.return_target_y = tile.center_y
                        enemy.return_tile = tile    # optional, um direction später zu lesen
                        try:
                            self.following_Enemy_sprite_list.remove(enemy)
                        except ValueError:
                            pass
                        if enemy not in self.retourning_list:
                            self.retourning_list.append(enemy)
                        # sofort weiter (keine weitere Verfolgung diesen Frame)
                        continue

        # 4) RETOURNING: zurück zur gespeicherten return_target_x/y und dann wieder einreihen
        for enemy in list(self.retourning_list):
            tx = getattr(enemy, "return_target_x", enemy.center_x)
            ty = getattr(enemy, "return_target_y", enemy.center_y)

            dx = tx - enemy.center_x
            dy = ty - enemy.center_y
            d = math.hypot(dx, dy)

            if d > 5:
                # BERECHNUNG DER RICHTUNG (für die Rotation wichtig!)
                enemy.change_x = (dx / d) 
                enemy.change_y = (dy / d)
                
                enemy.center_x += enemy.change_x * self.path_enemy_speed
                enemy.center_y += enemy.change_y * self.path_enemy_speed
            else:
                # Snap auf Tilezentrum
                enemy.center_x, enemy.center_y = tx, ty

                # Wenn wir die Tile erreicht haben: Setze Richtung des Pfades
                if hasattr(enemy, "return_tile") and enemy.return_tile is not None:
                    dir_prop = enemy.return_tile.properties.get("direction", None)
                    # Hier nutzen wir deine Hilfsfunktion
                    vx, vy = self._direction_to_vector(dir_prop)
                    enemy.change_x, enemy.change_y = vx, vy
                
                # Zurück in Patrouillenliste
                if enemy in self.retourning_list:
                    self.retourning_list.remove(enemy)
                if enemy not in self.path_Enemy_sprite_list:
                    self.path_Enemy_sprite_list.append(enemy)

            # WICHTIG: Update Rotation und Animation NACHDEM change_x/y gesetzt wurden
            self.update_enemy_rotation(enemy)
            self.update_enemy_animation(enemy, self.window.delta_time)
            

        # 5) Kugeln & Schrott (wie zuvor)
        for bullet in self.bullet_sprite_list:
            bullet_speed = 25
            if hasattr(self, "currentWeapon"):
                bullet_speed = 15 + self.Daten.get_one_weapon_data(self.currentWeapon, "speed") * 1.25
            if hasattr(bullet, "d") and bullet.d != 0:
                bullet.center_x += (bullet.dx / bullet.d) * bullet_speed
                bullet.center_y += (bullet.dy / bullet.d) * bullet_speed

        for scrap in self.scrap_list:
            dx, dy = player.center_x - scrap.center_x, player.center_y - scrap.center_y
            d = math.hypot(dx, dy)
            if d != 0:
                scrap.center_x += (dx / d) * 15
                scrap.center_y += (dy / d) * 15

    def update_enemy_rotation(self, sprite):
        """Rotate enemy sprite to align with current movement vector."""
        dx = getattr(sprite, "change_x", 0)
        dy = getattr(sprite, "change_y", 0)

        if dx != 0 or dy != 0:
            angle_rad = math.atan2(-dy, dx)
            sprite.angle = math.degrees(angle_rad) - 90

    
    def update_enemy_animation(self, sprite, delta_time):
        """Cycle enemy textures using a fixed animation timer."""
        sprite.animation_timer += delta_time

        if sprite.animation_timer >= 0.12:
            sprite.animation_timer = 0
            sprite.current_texture = (sprite.current_texture + 1) % len(sprite.textures)
            sprite.texture = sprite.textures[sprite.current_texture]

    def kill_all_enemys(self):
        """Force-kill every enemy regardless of list membership."""
        for enemy in list(self.following_Enemy_sprite_list):
            self.enemy_death(enemy)
        for enemy in list(self.path_Enemy_sprite_list):
            self.enemy_death(enemy)
        for enemy in list(self.retourning_list):
            self.enemy_death(enemy)


    def all_collision_checks(self, player):
        """Process bullet-vs-enemy, player-vs-scrap, and enemy-vs-player collisions."""
        # BULLET ENEMY COLLISION
        for bullet in list(self.bullet_sprite_list):
            collides_path = arcade.check_for_collision_with_list(bullet, self.path_Enemy_sprite_list)
            collides_follow = arcade.check_for_collision_with_list(bullet, self.following_Enemy_sprite_list)
            
            if collides_path or collides_follow:
                bullet.kill()
                for enemy in collides_path:
                    if self.overwrite_damage == None:
                        enemy.health -= self.Daten.get_one_weapon_data(self.currentWeapon, "damage")
                    else:
                        enemy.health -= self.overwrite_damage
                    if enemy.health <= 0:
                        self.enemy_death(enemy)

                for enemy in collides_follow:
                    if self.overwrite_damage == None:
                        enemy.health -= self.Daten.get_one_weapon_data(self.currentWeapon, "damage")
                    else:
                        enemy.health -= self.overwrite_damage
                    if enemy.health <= 0:
                        self.enemy_death(enemy)  

        # SCRAP PLAYER COLLISION
        collision_scrap = arcade.check_for_collision_with_list(player, self.scrap_list)
        for scrap in collision_scrap:
            self.Daten.change_data("Schrott", 5)
            scrap.kill()

        # ENEMY PLAYER COLLISION
        if arcade.check_for_collision_with_list(player, self.path_Enemy_sprite_list) or arcade.check_for_collision_with_list(player, self.following_Enemy_sprite_list):
            if self.Daten.get_one_data("Health") > 0:
                self.Daten.change_data("Health", -0.5)
            elif self.Daten.get_one_data("Health") <= 0 and self.player_is_dead == False:
                self.player_is_dead = True
                return True
        
    def get_all_enemy_lists(self):
        """Expose all enemy sprite lists for UI/debug rendering."""
        return self.path_Enemy_sprite_list, self.following_Enemy_sprite_list, self.retourning_list
    
            

    def enemy_death(self, enemy):
        """Handle enemy death: spawn scrap and remove enemy sprite."""
        for i in range(3):
            scrap = arcade.Sprite(asset_path("assets/sprites/scrap.png"))
            scrap.center_x = enemy.center_x + random.randint(0, 20)
            scrap.center_y = enemy.center_y + random.randint(0, 20)
            scrap.scale = 0.5
            self.scrap_list.append(scrap)
        enemy.kill()

    def player_shoot(self, x, y):
        """Spawn and launch a bullet if weapon fire-rate cooldown allows it."""
        current_time = time.monotonic()
        self.currentWeapon = self.Daten.get_one_data("CurrentWeapon")
        if (current_time - self.last_shoot_time) >= self.Daten.get_one_weapon_data(self.currentWeapon, "speed"):
            arcade.play_sound(self.sound_shot, volume=int(self.Daten.get_one_data("SoundVolume")), loop=False)
            bullet = arcade.Sprite(asset_path("assets/sprites/bullet.png"))
            bullet.scale = 1.5
            bullet.position = self.player.position
            bullet.dx, bullet.dy = x - self.player.center_x, y - self.player.center_y
            bullet.d = math.hypot(bullet.dx, bullet.dy)
            
            if bullet.d > 0:
                self.bullet_sprite_list.append(bullet)
                self.last_shoot_time = current_time
