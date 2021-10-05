
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

import pygame as pg
from collision import *
from settings import *

class Bullet:
    radius = 10

    def __init__(self, game, x, y, angle, tag):
        self.game = game
        self.pos = pg.Vector2(x, y)
        self.speed = 800
        self.angle = angle
        self.lifespan = 1
        self.counter = 0
        self.collided = False
        self.tag = tag
        self.colors = {
            "player": self.game.get_color("primary"),
            "enemy": self.game.get_color("secondary"),
        }
        self.collision_obj = Circle(Vector(*self.pos), self.radius)

    def update(self, dt):
        self.pos.x += math.cos(self.angle) * self.speed * dt
        self.pos.y += math.sin(self.angle) * self.speed * dt
        self.counter += dt
        
        # Collision with the map
        self.collision_obj.pos.x = self.pos.x
        self.collision_obj.pos.y = self.pos.y
        if self.game.level_manager.current_map().poly_collide(self.collision_obj):
            self.collided = True

        # Collision with enemies
        for i, e in enumerate(self.game.enemy_manager.entities):
            if self.tag == "player" and collide(self.collision_obj, e.collision_obj):
                self.collided = True
                e.on_collision_with_bullet(i)
                break
                
        if self.tag == "enemy" and collide(self.collision_obj, self.game.player.collision_obj):
            self.collided = True
            self.game.player.die("Try to dodge the bullets next time!")

    def is_dead(self):
        if self.collided or self.counter > self.lifespan:
            self.game.particle_manager.generate(*self.pos, self.colors[self.tag]);
            sound_effects["explode"].play()
            return True

    def draw(self, screen):
        pg.draw.circle(screen, self.colors[self.tag], self.pos, self.radius)