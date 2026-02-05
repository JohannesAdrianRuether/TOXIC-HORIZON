import arcade, time, random, math

class MovementEngine():
    def __init__(self, scene, camera, window, Daten):
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

    def player_movement(self, player, keys_down, dash_x, dash_y, dash_decay, delta_time):
        self.player = player
        speed = 300 * delta_time 
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
        self.following_Enemy_sprite_list = arcade.SpriteList()
        self.follow_enemy_speed = 4
        self.path_Enemy_sprite_list = arcade.SpriteList()
        self.path_enemy_speed = 5

        for i in range(2):
            enemy = arcade.Sprite()
            enemy.scale = 3

            # --- TEXTURES EINMAL LADEN ---
            enemy.textures = [
                arcade.load_texture("sprites/enemy2/Drone1.png"),
                arcade.load_texture("sprites/enemy2/Drone2.png")
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


        for i in range(8):
            enemy = arcade.Sprite()
            enemy.scale = 2

            # --- TEXTURES EINMAL LADEN ---
            enemy.textures = [
                arcade.load_texture("sprites/spider/spider1.png"),
                arcade.load_texture("sprites/spider/spider2.png"),
                arcade.load_texture("sprites/spider/spider3.png"),
                arcade.load_texture("sprites/spider/spider4.png"),
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


        
        spawner = self.scene["spawns"]
        FollowEnemySpawner = [s for s in spawner if s.properties.get("spawn") == 'enemy1']
        PathEnemySpawnerONE = [s for s in spawner if s.properties.get("spawn") == 'enemy2']

        for enemy in self.following_Enemy_sprite_list:
            spawn = FollowEnemySpawner.pop()
            enemy.center_x, enemy.center_y = spawn.center_x, spawn.center_y

        for enemy in self.path_Enemy_sprite_list:
            spawn = PathEnemySpawnerONE.pop()
            enemy.center_x, enemy.center_y = spawn.center_x, spawn.center_y

    def draw_enemys(self):
        self.following_Enemy_sprite_list.draw(pixelated=True)
        self.path_Enemy_sprite_list.draw(pixelated=True)
        self.bullet_sprite_list.draw(pixelated=True)
        self.scrap_list.draw(pixelated=True)
        self.retourning_list.draw(pixelated=True)

    def _direction_to_vector(self, direction):
        # Helper: direction string -> (vx, vy)
        if direction == "left": return -1, 0
        if direction == "right": return 1, 0
        if direction == "up": return 0, 1
        if direction == "down": return 0, -1
        return 0, 0

    def run_enemy_movement(self, player):
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
            self.update_enemy_rotation(enemy)
            self.update_enemy_animation(enemy, self.window.delta_time)
            tx = getattr(enemy, "return_target_x", enemy.center_x)
            ty = getattr(enemy, "return_target_y", enemy.center_y)

            dx = tx - enemy.center_x
            dy = ty - enemy.center_y
            d = math.hypot(dx, dy)

            if d > 5:
                enemy.center_x += (dx / d) * self.path_enemy_speed
                enemy.center_y += (dy / d) * self.path_enemy_speed
            else:
                # Snap auf Tilezentrum
                enemy.center_x, enemy.center_y = tx, ty

                # Wenn wir die Tile haben: setze change_x/change_y nach tile.direction
                if hasattr(enemy, "return_tile") and enemy.return_tile is not None:
                    dir_prop = enemy.return_tile.properties.get("direction", None)
                    if dir_prop == "left": enemy.change_x, enemy.change_y = -1, 0
                    elif dir_prop == "right": enemy.change_x, enemy.change_y = 1, 0
                    elif dir_prop == "up": enemy.change_x, enemy.change_y = 0, 1
                    elif dir_prop == "down": enemy.change_x, enemy.change_y = 0, -1
                    else:
                        enemy.change_x, enemy.change_y = 0, 0
                else:
                    enemy.change_x, enemy.change_y = getattr(enemy, "change_x", 0), getattr(enemy, "change_y", 0)

                # Zurück in Patrouillenliste
                try:
                    self.retourning_list.remove(enemy)
                except ValueError:
                    pass
                if enemy not in self.path_Enemy_sprite_list:
                    self.path_Enemy_sprite_list.append(enemy)
            

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
        dx = getattr(sprite, "change_x", 0)
        dy = getattr(sprite, "change_y", 0)

        if dx != 0 or dy != 0:
            angle_rad = math.atan2(-dy, dx)
            sprite.angle = math.degrees(angle_rad) - 90

    
    def update_enemy_animation(self, sprite, delta_time):
        sprite.animation_timer += delta_time

        if sprite.animation_timer >= 0.12:   # ≈ 8 FPS
            sprite.animation_timer = 0
            sprite.current_texture = (sprite.current_texture + 1) % len(sprite.textures)
            sprite.texture = sprite.textures[sprite.current_texture]



    def all_collision_checks(self, player):
        # BULLET ENEMY COLLISION
        for bullet in list(self.bullet_sprite_list):
            collides_path = arcade.check_for_collision_with_list(bullet, self.path_Enemy_sprite_list)
            collides_follow = arcade.check_for_collision_with_list(bullet, self.following_Enemy_sprite_list)
            
            if collides_path or collides_follow:
                bullet.kill()
                for enemy in collides_path:
                    enemy.health -= self.Daten.get_one_weapon_data(self.currentWeapon, "damage")
                    if enemy.health <= 0:
                        self.enemy_death(enemy)    
                for enemy in collides_follow:
                    enemy.health -= self.Daten.get_one_weapon_data(self.currentWeapon, "damage")
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
        return self.path_Enemy_sprite_list, self.following_Enemy_sprite_list, self.retourning_list
    
            

    def enemy_death(self, enemy):
        for i in range(3):
            scrap = arcade.Sprite("sprites/scrap.png")
            scrap.center_x = enemy.center_x + random.randint(0, 20)
            scrap.center_y = enemy.center_y + random.randint(0, 20)
            scrap.scale = 0.5
            self.scrap_list.append(scrap)
        enemy.kill()

    def player_shoot(self, x, y):
        if not hasattr(self, 'player') or self.player is None:
            return

        current_time = time.monotonic()
        self.currentWeapon = self.Daten.get_one_data("CurrentWeapon")
        if (current_time - self.last_shoot_time) >= self.Daten.get_one_weapon_data(self.currentWeapon, "speed"):
            bullet = arcade.Sprite("sprites/bullet.png")
            bullet.scale = 1.5
            bullet.position = self.player.position
            bullet.dx, bullet.dy = x - self.player.center_x, y - self.player.center_y
            bullet.d = math.hypot(bullet.dx, bullet.dy)
            
            if bullet.d > 0:
                self.bullet_sprite_list.append(bullet)
                self.last_shoot_time = current_time
