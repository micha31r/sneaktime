import random
import pygame as pg
from collision import *

import inventory
import bullet
import ui
from settings import *
from scripts import *

class Player:
    def __init__(self, game):
        self.game = game

        self.pos = pg.Vector2(0, 0)
        self.vel = pg.Vector2()
        self.max_vel = 260
        self.friction = 0.85
        self.mode = "move"
        self.alive = True
        self.completed_level = False

        # Game stats
        self.gameplay_timer = 0
        self.death_count = 0

        self.inventory = inventory.InventoryManager()

        # Length from the center
        self.aim_line_length = 50
        self.can_shoot = False
        self.shoot_counter = 0
        self.angle = 0

        # Sprites & Animation
        self.img = pg.image.load(rs_dir + "/characters/player.png").convert_alpha()
        self.img_w, self.img_h = self.img.get_size()
        self.enemy_img = pg.image.load(rs_dir + "/characters/enemy.png").convert_alpha()

        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj = Circle(Vector(*self.c_pos), self.img_w/2)

        self.has_armour = False
        self.transparent_surface = pg.Surface(WORLD_SIZE, pg.SRCALPHA)
        self.idle_armour_radius = self.img_w * 0.6
        self.idle_armour_counter = 0
        self.active_armour_radius = 0
        self.max_active_armour_radius = self.img_w * 3
        self.active_armour_angle = random.uniform(0, math.pi*2)
        self.armour_is_active = False

        # Interface stuff
        self.death_text = ""
        self.show_retry_message = True
        self.show_success_message = True

    def reset(self):
        self.mode = "move"
        self.alive = True
        self.can_shoot = False
        self.shoot_counter = 0
        self.angle = 0
        self.inventory = inventory.InventoryManager()
        self.show_retry_message = True
        self.show_success_message = True
        self.retry_message = None
        self.success_message = None
        self.completed_level = False

    def die(self, text=None):
        if self.alive:
            if self.has_armour:
                self.armour_is_active = True
            else:
                if text:
                    self.death_text = text + " Press SPACE to retry"
                else:
                    self.death_text = "Press SPACE to retry"
                self.alive = False
                self.death_count += 1
                self.game.change_speed(0, 1)
                self.game.particle_manager.generate(*self.c_pos, (128, 35, 255), (10, 20))

    def shoot(self):
        if self.can_shoot:
            if self.inventory.has_powerup("shotgun"):
                self.game.particle_manager.add(bullet.Bullet(self.game, *self.c_pos, self.angle, "player"))
                for i in range(4):
                    self.game.particle_manager.add(bullet.Bullet(self.game, *self.c_pos, self.angle + random.uniform(-1,1), "player"))
            else:
                self.game.particle_manager.add(bullet.Bullet(self.game, *self.c_pos, self.angle, "player"))
            # Set kickback velocity (opposite to the bullet's velocity)
            self.vel.x -= math.cos(self.angle) * self.max_vel
            self.vel.y -= math.sin(self.angle) * self.max_vel
            # Shake camera
            self.game.camera.shake(100)
            self.can_shoot = False

    def boss_collide(self):
        all_collisions = []
        if self.game.level_manager.current_level == len(self.game.level_manager.levels) - 1:
            for e in self.game.enemy_manager.entities:
                if type(e).__name__ == "Boss":
                    r = Response()
                    if collide(self.collision_obj, e.collision_obj, r):
                        all_collisions.append(r.overlap_v)
        return all_collisions

    def move(self, dt):
        # Player collision and movement
        dx = self.vel.x * dt
        dy = self.vel.y * dt

        self.pos.x += dx
        self.pos.y += dy

        # Update collision object
        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj.pos = Vector(*self.c_pos)

        all_collisions = self.boss_collide() + self.game.level_manager.current_map().poly_collide(self.collision_obj, capture_all=True, exclude_layer_name="exit")
        if all_collisions:
            for c in all_collisions:
                self.pos.x -= c.x
                self.pos.y -= c.y
                self.c_pos = center(*self.pos, self.img_w, self.img_h)
                self.collision_obj.pos = Vector(*self.c_pos)
                # pass
            self.vel.x = 0
            self.vel.y = 0

        # Decrease velocity
        self.vel.x *= self.friction
        self.vel.y *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel.x) < 0.05:
            self.vel.x = 0
        if abs(self.vel.y) < 0.05:
            self.vel.y = 0

    def update(self, dt):
        keys = pg.key.get_pressed()

        if self.alive:
            self.gameplay_timer += dt / self.game.speed
            self.inventory.update(dt)

            # Switch to the next level if player has collected all required items and has reached the exit
            lv_mger = self.game.level_manager
            met_requirements = True
            required_items = lv_mger.current_level_obj()["items"].items()
            for k,v in required_items:
                if len(self.inventory.get_item(k)) < v:
                    met_requirements = False
            if met_requirements:
                if lv_mger.current_map().poly_collide(self.collision_obj, target_layer_name="exit"):
                    if not self.completed_level:
                        self.game.particle_manager.generate(*self.c_pos, (128, 35, 255), (10, 20))
                        self.game.change_speed(0, 1)
                        self.completed_level = True
                    else:
                        if self.game.speed < 0.01:
                            if self.show_success_message:
                                self.success_message = self.game.interface_manager.message("Level complete! Press SPACE to continue", False)
                                self.show_success_message = False
                            elif self.success_message.text.index == len(self.success_message.text.text):
                                if keys[pg.K_SPACE]:
                                    self.game.speed = 1
                                    self.game.target_speed = 1
                                    lv_mger.next()
                                    return

            # Player controls
            if not self.completed_level:
                # Update shoot counter
                if not self.can_shoot:
                    self.shoot_counter += dt
                    if self.shoot_counter > 0.5:
                        self.can_shoot = True
                        self.shoot_counter = 0

                if self.can_shoot:
                    # Reduce the global game speed by 3/4 when in aiming mode
                    if keys[pg.K_SPACE]:
                        self.game.change_speed(0.25)
                        self.mode = "aim"
                    elif self.mode == "aim": # If key is just released and the control mode hasn't changed
                        self.game.change_speed(1)
                        self.shoot()
                        self.mode = "move"

                if self.mode == "move":
                    if keys[pg.K_LEFT]:
                        self.vel.x = -self.max_vel
                    elif keys[pg.K_RIGHT]:
                        self.vel.x = self.max_vel
                    if keys[pg.K_UP]:
                        self.vel.y = -self.max_vel
                    elif keys[pg.K_DOWN]:
                        self.vel.y = self.max_vel
                elif self.mode == "aim":
                    # Aiming will not affected by the game speed unless the player is dead
                    if self.alive: aim_speed = dt / self.game.speed
                    else: aim_speed = dt
                    if keys[pg.K_LEFT]:
                        self.angle -= 5 * aim_speed
                    elif keys[pg.K_RIGHT]:
                        self.angle += 5 * aim_speed
                    # Limit angle
                    if self.angle < 0:
                        self.angle = math.radians(360) + self.angle
                    if self.angle > math.radians(360):
                        self.angle = self.angle - math.radians(360)
        else:
            if self.game.speed < 0.01:
                if self.show_retry_message:
                    self.retry_message = self.game.interface_manager.message(self.death_text, False)
                    self.show_retry_message = False
                elif self.retry_message.text.index == len(self.retry_message.text.text):
                    if keys[pg.K_SPACE]:
                        self.game.mode = "level"
                        self.game.speed = 1
                        self.game.target_speed = 1
                        self.game.level_screen = ui.LevelScreen(self.game)
                        return

        # Check if player has armour
        self.has_armour = bool(self.inventory.has_powerup("armour"))

        # Change the size of the idle armour indicator
        if self.has_armour:
            self.idle_armour_counter += 10 * dt
            # Change the size of the active armour indicator
            if self.armour_is_active:
                diff = self.max_active_armour_radius - self.active_armour_radius
                self.active_armour_radius += diff * 10 * dt
                if diff < 0.01:
                    self.armour_is_active = False
                    self.active_armour_radius = 0
                    self.active_armour_angle = random.uniform(0, math.pi*2)
        else:
            self.idle_armour_counter = 0
            self.armour_is_active = False

        # Move and track player
        self.move(dt)
        self.game.camera.track((self.pos.x, self.pos.y, self.img_w, self.img_h))

    def draw(self, screen):
        if self.mode == "aim":
            # Draw aiming lines
            end_pos = pg.Vector2(self.c_pos.x + math.cos(self.angle)*self.aim_line_length, self.c_pos.y + math.sin(self.angle)*self.aim_line_length)
            pg.draw.circle(screen, (128, 35, 255), end_pos, 5)

        # Draw self
        if self.inventory.has_powerup("disguise"):
            screen.blit(self.enemy_img, self.pos)
        else:
            screen.blit(self.img, self.pos)

        # Draw idle armour
        if self.has_armour:
            change = (math.sin(self.idle_armour_counter) + 1) * 10
            pg.draw.circle(screen, (128, 35, 255), self.c_pos, self.idle_armour_radius + change, 2)

        # Draw active armour
        if self.armour_is_active:
            opacity = (self.max_active_armour_radius - self.active_armour_radius)
            draw_ngon(self.transparent_surface, (128, 35, 255, opacity), 5, self.active_armour_radius, self.c_pos, self.active_armour_angle)
            screen.blit(self.transparent_surface, (0,0))
            self.transparent_surface.fill((255,255,255,0))

