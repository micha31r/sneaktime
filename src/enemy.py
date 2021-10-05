
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
from collision import *
from settings import *
from scripts import *

class EnemyManager:
    def __init__(self, game):
        self.game = game
        self.detect_outside_FOV = False
        self.entities = []
        self.transparent_surface = pg.Surface(WORLD_SIZE, pg.SRCALPHA)

    def add(self, e):
        self.entities.append(e)

    def update(self, dt):
        for i, e in reversed(list(enumerate(self.entities))):
            e.update(dt, self.detect_outside_FOV)
            if e.is_dead():
                sound_effects["splatter"].play()
                self.game.player.kill_count_change += 1
                del self.entities[i]

    def reset(self):
        self.detect_outside_FOV = False
        self.entities = []

    def draw(self, screen):
        # Draw transparent surface
        screen.blit(self.transparent_surface, (0,0))
        self.transparent_surface.fill((0, 0, 0, 0))

        # Draw enemies
        for e in self.entities:
            e.draw(screen)


# Used as a signal so player can only complete the level after killing the boss
class BossDeathComfirmation:
    def __init__(self):
        self.name = "boss_death_comfirmation"


class Boss:
    def __init__(self, game, x, y):
        self.game = game
        self.health = 10
        self.shoot_angle = random.randint(0, 360)
        self.shoot_timer = random.uniform(0.5, 3)
        self.explosion_counter = 0
        self.explosion_timer = random.uniform(0.2, 1)

        # Sprites & Animation
        self.load_sprite()
        self.img_w, self.img_h = self.img.get_size()

        self.pos = pg.Vector2(x, y)
        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj = Circle(Vector(*self.c_pos), self.img_w/2)
        self.detection_obj = Circle(Vector(*self.c_pos), self.img_w)

        self.defeated = False

    def load_sprite(self):
        self.img = pg.image.load(self.game.get_themed_path("characters", "boss.png")).convert_alpha()
        self.img_defeated = pg.image.load(self.game.get_themed_path("characters", "boss_defeated.png")).convert_alpha()

    def is_dead(self):
        pass

    def on_collision_with_bullet(self, i):
        self.health -= 1
        if self.health > 0:
            # Shoot back immediately
            self.shoot()
            self.shoot_timer = random.uniform(0.5, 3)
            self.shoot_angle = random.randint(0, 360)

    def shoot(self):
        for i in range(0, 360, 60):
            self.game.particle_manager.add(bullet.Bullet(self.game, *self.c_pos, math.radians(i+self.shoot_angle), "enemy"))
        
    def update(self, dt, _):
        if self.health <= 0:
            if self.explosion_counter < 9:
                self.explosion_timer -= dt
                if self.explosion_timer < 0:
                    self.explosion_timer = self.explosion_timer = random.uniform(0.2, 1)
                    self.explosion_counter += 1
                    self.game.particle_manager.generate(*self.c_pos, self.game.get_color("primary"), (20, 30))
                    self.game.particle_manager.generate(*self.c_pos, self.game.get_color("third"), (20, 30))
                    sound_effects["explode"].play()
                self.game.camera.track((self.pos.x, self.pos.y, self.img_w, self.img_h))
            elif not self.defeated:
                self.defeated = True
                self.game.interface_manager.message("Mission accomplished, the technology has been destroyed", typing_effect=False)
                self.game.player.inventory.add_item(BossDeathComfirmation())
        else:
            self.shoot_timer -= dt
            if self.shoot_timer < 0 and collide(self.detection_obj, self.game.player.collision_obj):
                self.shoot()
                self.shoot_timer = random.uniform(0.5, 3)
                self.shoot_angle = random.randint(0, 360)

    def draw(self, screen):
        if self.defeated:
            screen.blit(self.img_defeated, self.pos)
        else:
            screen.blit(self.img, self.pos)


class Enemy:
    def __init__(self, game, x, y):
        self.game = game
        self.pos = pg.Vector2(x, y)
        self.vel = pg.Vector2()
        self.max_vel = random.randint(200, 300)
        self.friction = 0.9
        self.mode = "move"
        self.alive = True

        # Length from the center
        self.aim_line_length = 50
        self.can_shoot = False
        self.shoot_counter = 0
        self.angle = 0

        # Sprites & Animation
        self.load_sprite()
        self.img_w, self.img_h = self.img.get_size()

        # Field of view
        v = Vector
        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj = Circle(v(*self.c_pos), self.img_w/2)
        self.angular_vel = 0
        self.FOV_points = [
            v(-self.img_w/2, 0),
            v(self.img_w/2, 0), 
            v(self.img_w*2, self.img_h*5), 
            v(-self.img_w*2, self.img_h*5), 
        ]
        self.FOV_obj = Poly(v(*self.c_pos), self.FOV_points, self.angle)
        # How long between each random turn in idle mode
        self.turn_delay_timer = random.uniform(0.5,2)

        self.trigger_lockdown_timer = 5

    def load_sprite(self):
        self.img = pg.image.load(self.game.get_themed_path("characters", "enemy.png")).convert_alpha()

    def is_dead(self):
        return not self.alive

    def on_collision_with_bullet(self, i):
        self.alive = False

    def move(self, dt):
        dx = self.vel.x * dt
        dy = self.vel.y * dt

        self.pos.x += dx
        self.pos.y += dy

        # Update collision object
        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj.pos = Vector(*self.c_pos)

        all_collisions = self.peer_collide() + self.game.level_manager.current_map().poly_collide( self.collision_obj, capture_all=True)
        if all_collisions:
            for c in all_collisions:
                self.pos.x -= c.x
                self.pos.y -= c.y
                self.c_pos = center(*self.pos, self.img_w, self.img_h)
                self.collision_obj.pos = Vector(*self.c_pos)
                # pass
            self.vel.x = 0
            self.vel.y = 0

        # Turn enemy
        self.FOV_obj.angle += self.angular_vel * dt

        # Decrease velocity
        self.vel.x *= self.friction
        self.vel.y *= self.friction
        self.angular_vel *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel.x) < 0.05:
            self.vel.x = 0
        if abs(self.vel.y) < 0.05:
            self.vel.y = 0

    def shoot(self):
        if self.can_shoot:
            self.game.particle_manager.add(bullet.Bullet(self.game, *self.c_pos, self.angle, "enemy"))
            # Set kickback velocity (opposite to the bullet's velocity)
            self.vel.x -= math.cos(self.angle) * self.max_vel
            self.vel.y -= math.sin(self.angle) * self.max_vel
            self.can_shoot = False

    def simulate_controls(self, dt, detect_outside_FOV):
        player = self.game.player
        dv = player.c_pos - self.c_pos

        detected_player = False
        
        if not player.inventory.has_powerup("disguise"):
            if detect_outside_FOV or (collide(self.game.player.collision_obj, self.FOV_obj) or (abs(dv.x) < self.img_w and abs(dv.y) < self.img_h)):
                detected_player = True
                
                if not self.game.level_manager.lockdown:
                    # Initiate lockdown after a few seconds delay
                    self.trigger_lockdown_timer -= dt
                    if self.trigger_lockdown_timer < 0:
                        self.game.level_manager.lockdown = True
                        self.trigger_lockdown_timer = 5

                # Set angular velocity
                # https://stackoverflow.com/questions/42258637/how-to-know-the-angle-between-two-vectors
                angle = math.atan2(self.c_pos.y-player.c_pos.y, self.c_pos.x-player.c_pos.x)
                rotated_angle = angle + math.radians(90)
                self.angle = angle + math.radians(180)
                a_diff = rotated_angle - self.FOV_obj.angle

                # Find the difference between two angles with sign
                # https://stackoverflow.com/questions/1878907/how-can-i-find-the-difference-between-two-angles
                da = math.atan2(math.sin(a_diff), math.cos(a_diff))
                self.angular_vel += da

                # Shoot
                # Only shoot if player is in direct line of sight
                v = Vector

                # Calculate how far the player is from the enemy
                l_diff = abs((v(*player.c_pos) - v(*self.c_pos)).ln())

                # Check for of the the player in the enemy's direct Line Of Sight
                LOS_poly_points = [
                    v(-bullet.Bullet.radius, 0),
                    v(bullet.Bullet.radius, 0),
                    v(bullet.Bullet.radius, l_diff),
                    v(-bullet.Bullet.radius, l_diff),
                ]
                LOS_poly = Poly(v(*self.c_pos), LOS_poly_points, rotated_angle)
                collision = self.game.level_manager.current_map().poly_collide(LOS_poly)
                # Shoot if there's not obstables in the way
                if not collision:
                    self.shoot()

                # Debug, draw aiming line
                # pg.draw.polygon(screen, (100,100,100, 32), LOS_poly.points)

                # Update shoot counter here so the enemy doesn't immediately shoot when it detects the player
                if not self.can_shoot:
                    self.shoot_counter += dt
                    if self.shoot_counter > 1:
                        self.can_shoot = True
                        self.shoot_counter = 0

                # Move the enemy
                self.vel = dv
                if self.vel.x > self.max_vel:
                    self.vel.x = self.max_vel
                elif self.vel.x < -self.max_vel:
                    self.vel.x = -self.max_vel
                if self.vel.y > self.max_vel:
                    self.vel.y = self.max_vel
                elif self.vel.y < -self.max_vel:
                    self.vel.y = -self.max_vel

        if not detected_player:
            # Turn the enemy randomly when not chasing the player (in idle mode)
            self.turn_delay_timer -= dt
            if abs(self.angular_vel) < 2 and self.turn_delay_timer < 0:
                self.turn_delay_timer = random.uniform(0.5, 2)
                self.angular_vel += random.uniform(-12,12) # Doesn't have to be in radians

    def peer_collide(self):
        all_collisions = []
        for e in self.game.enemy_manager.entities:
            if e != self:
                r = Response()
                if collide(self.collision_obj, e.collision_obj, r):
                    all_collisions.append(r.overlap_v)
        return all_collisions

    def update(self, dt, detect_outside_FOV):
        self.simulate_controls(dt, detect_outside_FOV)
        self.move(dt)
        self.FOV_obj.pos = Vector(*self.c_pos)

    def draw(self, screen):
        if self.mode == "aim":
            # Draw aiming lines
            end_pos = pg.Vector2(self.c_pos.x + math.cos(self.angle)*self.aim_line_length, self.c_pos.y + math.sin(self.angle)*self.aim_line_length)
            pg.draw.circle(screen, self.game.get_color("primary"), end_pos, 5)

        # Draw FOV area
        pg.draw.polygon(self.game.enemy_manager.transparent_surface, (*self.game.get_color("background"), 32), self.FOV_obj.points)

        # Draw self
        screen.blit(self.img, self.pos)