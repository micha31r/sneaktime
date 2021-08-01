import math
import pygame as pg

import tilemap
import enemy
import powerup
import trap
from settings import *

class LevelManager:
    def __init__(self, game, n=0):
        self.game = game
        self.lockdown = False
        self.lockdown_timer = 20
        self.lockdown_opacity_counter = 0
        self.current_level = n
        self.levels = [tilemap.TiledMap(game, "/tilemap.json")]
        self.transparent_surface = pg.Surface(WORLD_SIZE, pg.SRCALPHA)

    def current_map(self):
        return self.levels[self.current_level]

    def switch(self, n):
        self.current_level = n
        self.load_level(n)

    def load_level(self, n):
        spawners = self.current_map().spawners

        # Spawn enemies
        points = spawners["enemy"]
        for p in points:
            self.game.enemy_manager.add(enemy.Enemy(self.game, p[0], p[1]))

        # Spawn powerups
        # Disguise powerups
        points = spawners["disguise"]
        for p in points:
            self.game.powerup_manager.add(powerup.DisguisePowerUp(self.game, p[0], p[1]))

        # Shotgun powerups
        points = spawners["shotgun"]
        for p in points:
            self.game.powerup_manager.add(powerup.ShotgunPowerUp(self.game, p[0], p[1]))

        # Traps
        # Horizontal and vertical lasers
        points = spawners["laser_h"]
        for p in points:
            self.game.trap_manager.add(trap.LaserTrap(self.game, p[0], p[1], "horizontal"))

        points = spawners["laser_v"]
        for p in points:
            self.game.trap_manager.add(trap.LaserTrap(self.game, p[0], p[1], "vertical"))

        # Horizontal and vertical ninja stars
        points = spawners["ninja_star_h"]
        for p in points:
            self.game.trap_manager.add(trap.NinjaStarTrap(self.game, p[0], p[1], "horizontal"))

        points = spawners["ninja_star_v"]
        for p in points:
            self.game.trap_manager.add(trap.NinjaStarTrap(self.game, p[0], p[1], "vertical"))

    def update(self, dt):
        if self.lockdown:
            self.game.enemy_manager.detect_outside_FOV = True
            self.lockdown_timer -= dt
            self.lockdown_opacity_counter += dt
            # Deactivate lockdown when opacity is approximately 0 (50 + -1 * 50 = 0)
            if self.lockdown_timer < 0 and math.sin(self.lockdown_opacity_counter) < -0.9:
                # Code here to show restart menu
                self.lockdown = False
                self.lockdown_timer = 10
                self.lockdown_opacity_counter = 0

    def draw_lockdown_filter(self, screen):
        # Draw transparent red filter
        if self.lockdown:
            # Opacity ust be between 0 - 255
            opacity = 50 + math.sin(self.lockdown_opacity_counter * 4) * 50
            screen.blit(self.transparent_surface, (0,0))
            self.transparent_surface.fill((255,255,255,0))
            ww, wh = self.game.window.get_size()
            pg.draw.rect(self.transparent_surface, (255, 0, 76, opacity), (self.game.camera.pos.x-20, self.game.camera.pos.y-20, ww+40, wh+40))

    def draw(self, screen):
        self.current_map().draw(screen)