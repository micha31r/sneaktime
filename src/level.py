import math
import pygame as pg

import tilemap
import enemy
import item
import trap
import ui
from settings import *

class LevelManager:
    def __init__(self, game, n=0):
        self.game = game
        self.lockdown = False
        self.lockdown_timer = 20
        self.lockdown_opacity_counter = 0
        self.current_level = n
        self.levels = [
            {
                "items": {
                    "key": 1,
                },
                "map": tilemap.TiledMap(game, "/maps/tilemap1.json"),
            },
            {
                "items": {
                    "key": 3,
                    "boss_death_comfirmation": 1, # This must be set for the last level
                },
                "map": tilemap.TiledMap(game, "/maps/tilemap2.json"),
            },
        ]
        self.transparent_surface = pg.Surface(WORLD_SIZE, pg.SRCALPHA)

    def current_level_obj(self):
        return self.levels[self.current_level]

    def current_map(self):
        return self.levels[self.current_level]["map"]

    def switch(self, n):
        self.current_level = n
        self.game.mode = "level"
        self.game.level_screen = ui.LevelScreen(self.game)

    def next(self):
        if self.current_level < len(self.levels) - 1:
            self.switch(self.current_level + 1)
        else:
            # Show game complete screen if there are no more levels
            self.game.mode = "complete"
            self.game.complete_screen = ui.CompleteScreen(self.game)

    def load_level(self, n=None):
        if not n:
            n = self.current_level

        self.reset()
        self.game.player.reset()
        self.game.particle_manager.reset()
        self.game.enemy_manager.reset()
        self.game.item_manager.reset()
        self.game.trap_manager.reset()
        self.game.interface_manager.reset()

        spawners = self.current_map().spawners

        # Set player position
        x, y, _, _ = spawners["player"][0]
        self.game.player.pos = pg.Vector2(x, y)

        # Spawn enemies
        points = spawners["enemy"]
        for p in points:
            self.game.enemy_manager.add(enemy.Enemy(self.game, p[0], p[1]))

        points = spawners["boss"]
        for p in points:
            self.game.enemy_manager.add(enemy.Boss(self.game, p[0], p[1]))

        # Spawn items
        # Disguise items
        points = spawners["disguise"]
        for p in points:
            self.game.item_manager.add(item.DisguisePowerUp(self.game, p[0], p[1]))

        # Shotgun items
        points = spawners["shotgun"]
        for p in points:
            self.game.item_manager.add(item.ShotgunPowerUp(self.game, p[0], p[1]))

        # Armour items
        points = spawners["armour"]
        for p in points:
            self.game.item_manager.add(item.ArmourPowerUp(self.game, p[0], p[1]))

        # Items
        points = spawners["key"]
        for p in points:
            self.game.item_manager.add(item.KeyItem(self.game, p[0], p[1]))

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

        # Left, Right, Up and Down cameras
        points = spawners["camera_l"]
        for p in points:
            self.game.trap_manager.add(trap.CameraTrap(self.game, p[0], p[1], "left"))

        points = spawners["camera_r"]
        for p in points:
            self.game.trap_manager.add(trap.CameraTrap(self.game, p[0], p[1], "right"))

        points = spawners["camera_u"]
        for p in points:
            self.game.trap_manager.add(trap.CameraTrap(self.game, p[0], p[1], "up"))

        points = spawners["camera_d"]
        for p in points:
            self.game.trap_manager.add(trap.CameraTrap(self.game, p[0], p[1], "down"))

    def reset(self):
        self.lockdown = False
        self.lockdown_timer = 20
        self.lockdown_opacity_counter = 0

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

    def draw_filter(self, screen):
        if self.lockdown:
            # Draw transparent red filter
            # Opacity ust be between 0 - 255
            opacity = 50 + math.sin(self.lockdown_opacity_counter * 4) * 50
            # screen.blit(self.transparent_surface, (0,0))
            # self.transparent_surface.fill((255,255,255,0))
            ww, wh = self.game.window.get_size()
            pg.draw.rect(self.transparent_surface, (255, 0, 76, opacity), (self.game.camera.pos.x-20, self.game.camera.pos.y-20, ww+40, wh+40))
        screen.blit(self.transparent_surface, (0,0))
        self.transparent_surface.fill((255,255,255,0))

    def draw(self, screen):
        self.current_map().draw(screen)
        