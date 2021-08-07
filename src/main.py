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
            self.interface_manager.update(dt)
        elif self.mode == "complete":
            self.complete_screen.update(dt)

    def draw(self):
        if self.mode == "splash":
            self.splash_screen.draw(self.screen)
        elif self.mode == "story":
            self.story_screen.draw(self.screen)
        elif self.mode == "level":
            self.level_screen.draw(self.screen)
        elif self.mode == "main":
            self.level_manager.draw(self.screen)
            self.item_manager.draw(self.screen)
            self.player.draw(self.screen)
            self.enemy_manager.draw(self.screen)
            self.particle_manager.draw(self.screen)
            self.trap_manager.draw(self.screen)

            # Top layers
            self.level_manager.draw_filter(self.screen)
            self.player.inventory.draw(self.screen)
            self.interface_manager.draw(self.screen)
        elif self.mode == "complete":
            self.complete_screen.draw(self.screen)

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
            
            dt = self.clock.tick(60)
            # fps debug
            fps = round(1000/dt)
            if fps < 40:
                print(fps, "fps (Low)")
            dt /= 1000

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


game = GameManager()
game.event_loop()