
"""
-------------------------------------------------
    Project: Sneaktime
    Standard: 91906 (AS3.7)
    School: Tauranga Boys' College
    Author: Michael Ren
    Date: 05 OCT 2021
    Python: 3.9.6
    License: MIT
-------------------------------------------------
"""

import random
import pygame as pg
import inventory
import bullet
import ui
from collision import *
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
        self.sound_timer = 0.5
        self.first_shoot = False
        self.completed_tutorial = False

        # Game stats
        self.gameplay_timer = 0
        self.death_count = 0
        self.kill_count = 0
        self.kill_count_change = 0
        self.lockdown_count = 0
        self.lockdown_count_change = 0
        self.powerup_count = 0
        self.powerup_count_change = 0
        self.bullet_count = 0
        self.bullet_count_change = 0

        self.inventory = inventory.InventoryManager(self.game)

        # Length from the center
        self.aim_line_length = 50
        self.can_shoot = False
        self.shoot_counter = 0
        self.angle = 0

        # Sprites & Animation
        self.load_sprite()
        self.img_w, self.img_h = self.img.get_size()

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
        self.retry_message = None
        self.success_message = None
        self.inventory_message = None

    def load_sprite(self):
        self.img = pg.image.load(self.game.get_themed_path("characters", "player.png")).convert_alpha()
        self.enemy_img = pg.image.load(self.game.get_themed_path("characters", "enemy.png")).convert_alpha()

    def reset(self):
        self.mode = "move"
        self.alive = True
        self.can_shoot = False
        self.shoot_counter = 0
        self.first_shoot = False
        self.angle = 0
        self.inventory = inventory.InventoryManager(self.game)
        self.inventory_message = None
        self.retry_message = None
        self.success_message = None
        self.completed_level = False
        self.gameplay_timer = 0
        self.kill_count_change = 0
        self.lockdown_count_change = 0
        self.powerup_count_change = 0
        self.bullet_count_change = 0

    def die(self, text=None):
        if self.alive:
            if self.has_armour:
                if not self.armour_is_active:
                    self.armour_is_active = True
                    sound_effects["activate_forcefield"].play()
            else:
                if text:
                    self.death_text = text + " Press SPACE to retry"
                else:
                    self.death_text = "Press SPACE to retry"
                self.alive = False
                self.death_count += 1
                self.game.change_speed(0, 1)
                self.game.particle_manager.generate(*self.c_pos, self.game.get_color("primary"), (10, 20))
                if self.game.level_manager.lockdown:
                    self.game.level_manager.lockdown = False
                    sound_effects["alarm"].fadeout(1000)
                sound_effects["splatter"].play()

    def shoot(self):
        if self.can_shoot:
            sound_effects["shoot"].play()
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
        initial_pos = self.collision_obj.pos.copy()

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
            self.vel.x = 0
            self.vel.y = 0

        # Decrease velocity
        self.vel.x *= self.friction
        self.vel.y *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.1:
            self.vel.y = 0

        # Only increase sound timer if player has actually moved
        if (self.collision_obj.pos - initial_pos).ln() > 2:
            self.sound_timer -= dt

        self.footstep_sound(dt)

    def footstep_sound(self, dt):
        if self.sound_timer < 0:
            self.sound_timer = 0.5
            sound_effects["footstep"].play()

    def update(self, dt):
        keys = pg.key.get_pressed()

        if self.alive:
            self.gameplay_timer += dt / self.game.speed or 1
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
                        self.game.particle_manager.generate(*self.c_pos, self.game.get_color("primary"), (10, 20))
                        self.game.change_speed(0, 1)
                        self.completed_level = True
                        if self.game.level_manager.lockdown:
                            self.game.level_manager.lockdown = False
                            sound_effects["alarm"].fadeout(1000)
                        # Update stats
                        self.kill_count += self.kill_count_change
                        self.lockdown_count += self.lockdown_count_change
                        self.powerup_count += self.powerup_count_change
                        self.bullet_count += self.bullet_count_change
                        self.game.level_manager.record_stats()
                        self.game.save()
                        sound_effects["aura"].play()
                        # Reset stats
                        self.death_count = 0
                        self.kill_count = 0
                        self.lockdown_count = 0
                        self.powerup_count = 0
                        self.bullet_count = 0
                    else:
                        if self.game.speed < 0.01:
                            if not self.success_message:
                                sound_effects["success"].play()
                                self.success_message = self.game.interface_manager.message("Level complete! Press SPACE to continue", False)
                            elif self.success_message.text.index == len(self.success_message.text.text):
                                if keys[pg.K_SPACE]:
                                    sound_effects["confirm"].play()
                                    self.game.speed = 1
                                    self.game.target_speed = 1
                                    self.game.interface_manager.reset()
                                    lv_mger.next()
                                    return

            # Player controls
            if not self.completed_level and self.completed_tutorial:
                # Update shoot counter
                if not self.can_shoot:
                    self.shoot_counter += dt
                    if self.shoot_counter > 0.5:
                        self.can_shoot = True
                        self.shoot_counter = 0

                if self.can_shoot:
                    # Reduce the global game speed by 3/4 when in aiming mode
                    if keys[pg.K_SPACE]:
                        if not self.first_shoot and self.game.level_manager.current_level == 0:
                            self.first_shoot = True
                            self.game.interface_manager.message("Time slows down when you aim", typing_effect=False)
                        self.bullet_count_change += 1
                        self.game.change_speed(0.25)
                        self.mode = "aim"
                    elif self.mode == "aim": # If key is just released and the control mode hasn't changed
                        self.game.change_speed(1)
                        self.shoot()
                        self.mode = "move"

                if self.mode == "move":
                    # Set velocities
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
                    if self.alive: aim_speed = dt / self.game.speed or 1
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

                # Show inventory message when 'e' is pressed
                if keys[pg.K_e]:
                    if not self.inventory_message:
                        current = len(self.inventory.get_item("key")) # The amount the player has
                        total = self.game.level_manager.current_level_obj()["items"]["key"] # The total amount required
                        self.inventory_message = self.game.interface_manager.message(f"Collected keys ({current}/{total})", typing_effect=False)
                    else:
                        self.inventory_message.set_target_y()
                elif self.inventory_message:
                    self.inventory_message.set_target_y(-2)
                # Reset inventory messages
                if self.inventory_message and self.inventory_message.complete:
                    self.inventory_message = None
        else:
            if self.game.speed < 0.01:
                if not self.retry_message:
                    sound_effects["fail"].play()
                    self.retry_message = self.game.interface_manager.message(self.death_text, False)
                elif self.retry_message.text.index == len(self.retry_message.text.text):
                    if keys[pg.K_SPACE]:
                        sound_effects["confirm"].play()
                        # Allow the player to select level
                        self.game.mode = "select"
                        self.game.speed = 1
                        self.game.target_speed = 1
                        self.game.select_screen = ui.SelectScreen(self.game, False)
                        self.game.interface_manager.reset()
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
            pg.draw.circle(screen, self.game.get_color("primary"), end_pos, 5)

        # Draw self
        if self.inventory.has_powerup("disguise"):
            screen.blit(self.enemy_img, self.pos)
        else:
            screen.blit(self.img, self.pos)

        # Draw idle armour
        if self.has_armour:
            change = (math.sin(self.idle_armour_counter) + 1) * 10
            pg.draw.circle(screen, self.game.get_color("primary"), self.c_pos, self.idle_armour_radius + change, 2)

        # Draw active armour
        if self.armour_is_active:
            opacity = (self.max_active_armour_radius - self.active_armour_radius)
            if opacity > 255: opacity = 255
            elif opacity < 0: opacity = 0
            draw_ngon(self.transparent_surface, (*self.game.get_color("primary"), opacity), 5, self.active_armour_radius, self.c_pos, self.active_armour_angle)
            screen.blit(self.transparent_surface, (0, 0))
            self.transparent_surface.fill((0, 0, 0, 0))

