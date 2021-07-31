import random, math
import pygame as pg

from scripts import *

class TrapManager:
    def __init__(self, game):
        self.game = game
        self.traps = []

    def add(self, t):
        self.traps.append(t)

    def update(self, dt):
        for t in self.traps:
            t.update(dt)

    def draw(self, screen):
        for t in self.traps:
            t.draw(screen)


class LaserTrap:
    def __init__(self, game, x, y, direction):
        self.game = game
        self.pos = pg.Vector2(x, y)
        self.end_pos = pg.Vector2()
        self.direction = direction
        self.activated = False
        self.delay = random.randint(1,3)
        self.delay_timer = 0
        self.duration = random.randint(1,3)
        self.duration_timer = 0

        self.get_end_pos()

    def get_end_pos(self):
        game_map = self.game.level_manager.current_map()
        tw = game_map.tilewidth
        th = game_map.tileheight
        dx = 0
        dy = 0
        for i in range(32):
            if self.direction == "horizontal":
                dx += tw
            else:
                dy += th
            tile = game_map.get_tile(self.pos.x+dx, self.pos.y+dy, "Tile Layer 3") or game_map.get_tile(self.pos.x-dx, self.pos.y-dy, "Tile Layer 3")
            if tile and tile["tile_id"] == 17:
                self.pos = pg.Vector2(*center(*self.pos, tw, th))
                self.end_pos = pg.Vector2(*center(*tile["rect"]))
                break

    def update(self, dt):
        if self.activated:
            self.duration_timer -= dt
            if self.duration_timer < 0:
                self.activated = False
                self.duration_timer = self.duration
        else:
            self.delay_timer -= dt
            if self.delay_timer < 0:
                self.activated = True
                self.delay_timer = self.delay

    def draw(self, screen):
        if self.activated:
            pg.draw.line(screen, (0,0,0), self.pos, self.end_pos, 3)


