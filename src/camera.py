import random
import pygame as pg

from settings import *

class Camera:
    def __init__(self, game):
        self.game = game
        self.pos = pg.Vector2()
        self.scale = pg.Vector2(1, 1)
        self.vel = pg.Vector2()
        self.margin = 200
        self.max_vel = 400
        self.friction = 0.8
        self.do_track = True
        self.multiplier = 4
        self.do_shake = False
        self.shake_amount = 0
        self.shake_displacement = pg.Vector2()

    def shake(self, amount):
        self.do_shake = True
        self.shake_amount = amount

    def track(self, rect):
        if self.do_track:
            # Horzontal tracking
            a = self.pos.x + self.margin
            if rect[0] < a:
                self.vel.x = (rect[0] - a) * self.multiplier
            b = self.pos.x + self.width - self.margin
            if rect[0] + rect[2] > b:
                self.vel.x = ((rect[0] + rect[2]) - b) * self.multiplier

            # Verticle tracking
            c = self.pos.y + self.margin
            if rect[1] < c:
                self.vel.y = (rect[1] - c) * self.multiplier
            d = self.pos.y + self.height - self.margin
            if rect[1] + rect[3] > d:
                self.vel.y = ((rect[1] + rect[3]) - d) * self.multiplier

        # Set max velocity
        self.vel.x = self.vel.x if self.vel.x > -self.max_vel else -self.max_vel
        self.vel.x = self.vel.x if self.vel.x < self.max_vel else self.max_vel
        self.vel.y = self.vel.y if self.vel.y < self.max_vel else self.max_vel
        self.vel.y = self.vel.y if self.vel.y < self.max_vel else self.max_vel

    def reset(self):
        self.pos = pg.Vector2()
        self.shake_amount = 0
        self.shake_displacement = pg.Vector2()

    def update(self, dt):
        ww, wh = self.game.window.get_size()
        self.width = ww / self.scale.x
        self.height = wh / self.scale.x

        # Move camera
        self.pos += self.vel * dt

        # Limit position
        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x + ww > WORLD_SIZE[0]:
            self.pos.x = WORLD_SIZE[0] - ww
        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y + wh > WORLD_SIZE[1]:
            self.pos.y = WORLD_SIZE[1] - wh

        # Decrease velocity
        self.vel.x *= self.friction
        self.vel.y *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel.x) < 0.01:
            self.vel.x = 0
        if abs(self.vel.y) < 0.01:
            self.vel.y = 0

        # Remove previous displacement
        self.pos -= self.shake_displacement

        # Remove shake if too small
        if self.do_shake:
            self.shake_amount *= self.friction
            self.shake_displacement.x = random.randint(-10,10) * self.shake_amount * dt
            self.shake_displacement.y = random.randint(-10,10) * self.shake_amount * dt
            if self.shake_amount < 0.01:
                self.shake_amount = 0
                self.do_shake = False
                self.shake_displacement.x = 0
                self.shake_displacement.y = 0

        # Apply new displacement
        self.pos += self.shake_displacement

