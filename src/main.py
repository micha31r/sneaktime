
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

import sys, json, math, random, os
import pygame as pg
import camera
import ui
import level
import player
import enemy
import particle
import item
import trap
import theme
import tutorial
from settings import *

pg.init()
pg.display.set_caption("sneaktime")

class GameManager:
    def __init__(self):
        self.window = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE)
        self.screen = pg.Surface(WORLD_SIZE)
        self.clock = pg.time.Clock()
        self.mode = "splash"
        self.target_speed = 1
        self.speed = 1
        self.speed_change_constant = 4
        self.current_theme = "purple"

        # Game components
        self.camera = camera.Camera(self)
        self.splash_screen = ui.SplashScreen(self)
        self.level_manager = level.LevelManager(self)
        self.player = player.Player(self)
        self.enemy_manager = enemy.EnemyManager(self)
        self.particle_manager = particle.ParticleManager(self)
        self.item_manager = item.ItemManager(self)
        self.trap_manager = trap.TrapManager(self)
        self.interface_manager = ui.InterfaceManager(self)
        self.tutorial_manager = tutorial.TutorialManager(self)

    def get_themed_path(self, folder, file):
        return os.path.join(*[rs_dir, folder, self.current_theme, file])

    def get_theme(self):
        return theme.THEMES[self.current_theme]

    def get_color(self, key):
        return theme.THEMES[self.current_theme][key]

    def change_speed(self, speed, const=None):
        self.target_speed = speed
        if const:
            self.speed_change_constant = const

    def has_save(self):
        return os.path.isfile(cache_path)

    def save(self):
        p = self.player
        data = {
            "current_level": self.level_manager.unlocked_level,
            "level_stats": self.level_manager.level_stats,
        }
        with open(cache_path, 'w') as f:
            json.dump(data, f)

    def load(self):
        if self.has_save():
            with open(cache_path, 'r') as f:
                d = json.load(f)
                # Always resume from the "select" screen
                self.mode = "select"
                level = d["current_level"]
                if level < len(self.level_manager.levels) - 1:
                    level += 1
                self.level_manager.current_level = level
                self.level_manager.unlocked_level = level
                self.level_manager.level_stats = d["level_stats"]
                self.select_screen = ui.SelectScreen(self)
            self.interface_manager.message(f"You progress is resumed from the previous session", typing_effect=False)
            return True
            
    def update(self, dt):
        ds = self.target_speed - self.speed # Delta speed
        self.speed += ds * self.speed_change_constant * dt # Increase the constant to increase the speed change
        if abs(ds) < 0.01:
            self.speed_change_constant = 4 # Reset speed change constant
        dt *= self.speed # Change global game speed

        if self.mode == "splash":
            self.splash_screen.update(dt)
        elif self.mode == "story":
            self.story_screen.update(dt)
        elif self.mode == "select":
            self.select_screen.update(dt)
        elif self.mode == "level":
            self.level_screen.update(dt)
        elif self.mode == "main":
            self.camera.update(dt)
            self.level_manager.update(dt)
            self.player.update(dt)
            self.enemy_manager.update(dt)
            self.particle_manager.update(dt)
            self.item_manager.update(dt)
            self.trap_manager.update(dt)
            self.tutorial_manager.update(dt)
        elif self.mode == "complete":
            self.complete_screen.update(dt)
        self.interface_manager.update(dt)

    def draw(self):
        if self.mode == "splash":
            self.splash_screen.draw(self.screen)
        elif self.mode == "story":
            self.story_screen.draw(self.screen)
        elif self.mode == "select":
            self.select_screen.draw(self.screen)
        elif self.mode == "level":
            self.level_screen.draw(self.screen)
        elif self.mode == "main":
            self.level_manager.draw(self.screen)
            self.item_manager.draw(self.screen)
            self.player.draw(self.screen)
            self.enemy_manager.draw(self.screen)
            self.particle_manager.draw(self.screen)
            self.trap_manager.draw(self.screen)
            self.tutorial_manager.draw(self.screen)

            # Top layers
            self.level_manager.draw_filter(self.screen)
            self.player.inventory.draw(self.screen)
        elif self.mode == "complete":
            self.complete_screen.draw(self.screen)
        self.interface_manager.draw(self.screen)

    def event_loop(self):
        while 1:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.VIDEORESIZE:
                    w, h = event.size
                    w = 640 if w < 640 else w
                    h = 480 if h < 480 else h
                    self.window = pg.display.set_mode((w, h), pg.RESIZABLE)
            
            dt = self.clock.tick(60) / 1000
            # fps debug
            # fps = round(1000/dt)
            # if fps < 40:
            #     print(fps, "fps (Low)")
            # dt /= 1000

            self.update(dt)

            self.screen.fill(self.get_color("background"))
            self.draw()
            self.window.fill(self.get_color("background"))
            # Render main surface after scaling it by the scale factor
            sw, sh = self.screen.get_size()
            self.window.blit(
                pg.transform.scale(
                    self.screen,
                    (
                        int(sw*self.camera.scale.x),
                        int(sh*self.camera.scale.y)
                    )
                ), (0, 0), 
                (
                    self.camera.pos.x * self.camera.scale.x,
                    self.camera.pos.y * self.camera.scale.y,
                    self.window.get_width(), self.window.get_height()
                )
            )
            pg.display.flip()


try:
    game = GameManager()
    game.event_loop()
except KeyboardInterrupt:
    print("ctrl-c Keyboard Interrupt")

