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
        self.friction = 0.9
        self.mode = "move"
        self.alive = True

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
        self.death_message = ""
        self.show_retry_message = True

    def reset(self):
        self.mode = "move"
        self.alive = True
        self.can_shoot = False
        self.shoot_counter = 0
        self.angle = 0
        self.inventory = inventory.InventoryManager()
        self.show_retry_message = True

    def die(self, message=None):
        if self.alive:
            if self.has_armour:
                self.armour_is_active = True
            else:
                if message:
                    self.death_message = message + " Press SPACE to retry"
                else:
                    self.death_message = "Press SPACE to retry"
                self.alive = False
                self.game.change_speed(0, 1)
                self.game.particle_manager.generate(*self.c_pos, (128, 35, 255), (10, 20))

    def shoot(self):
        if self.can_shoot:
            if self.inventory.has_item("shotgun"):
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

    def move(self, dt):
        # Player collision and movement
        dx = self.vel.x * dt
        dy = self.vel.y * dt

        self.pos.x += dx
        self.pos.y += dy

        # Update collision object
        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj.pos = Vector(*self.c_pos)

        all_collisions = self.game.level_manager.current_map().poly_collide(self.collision_obj, capture_all=True)
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
            self.inventory.update(dt)

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
                    self.game.interface_manager.message(self.death_message, False)
                    self.show_retry_message = False
                if keys[pg.K_SPACE]:
                    self.game.mode = "level"
                    self.game.speed = 1
                    self.game.target_speed = 1
                    self.game.level_screen = ui.LevelScreen(self.game)
                    self.game.camera.reset()
                return

        # Check if player has armour
        self.has_armour = bool(self.inventory.has_item("armour"))

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
        if self.inventory.has_item("disguise"):
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

