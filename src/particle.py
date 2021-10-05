
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

import random, math
import pygame as pg

class ParticleManager:
    def __init__(self, game):
        self.game = game
        self.particles = []

    def add(self, p):
        self.particles.append(p)

    def generate(self, x, y, color, minmax=(5, 10)):
        for i in range(random.randint(*minmax)):
            self.game.particle_manager.add(Particle(x, y, color))

    def update(self, dt):
        for i, p in reversed(list(enumerate(self.particles))):
            p.update(dt)
            if p.is_dead() == True:
                del self.particles[i]

    def reset(self):
        self.particles = []

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)


class Particle:
    def __init__(self, x, y, color=(0,0,0)):
        self.pos = pg.Vector2(x, y)
        self.speed = random.randint(200, 400)
        self.radius = random.randint(4, 8)
        self.angle = math.radians(random.randint(0, 360))
        self.color = color
        self.lifespan = random.uniform(0.3, 1)
        self.counter = 0

    def is_dead(self):
        if self.counter > self.lifespan:
            return True

    def update(self, dt):
        self.pos.x += math.cos(self.angle) * self.speed * dt
        self.pos.y += math.sin(self.angle) * self.speed * dt
        self.counter += dt
        self.radius -= (self.radius / self.lifespan) * dt

    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.pos, self.radius)