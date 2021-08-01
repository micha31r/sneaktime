import sys, json, math, random
import pygame as pg
from os import path

import camera
import ui
import level
import player
import enemy
import particle
import powerup
import trap
from settings import *

pg.init()
pg.display.set_caption("BreakIn()")

class GameManager:
    def __init__(self):
        self.window = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE)
        self.screen = pg.Surface(WORLD_SIZE)
        self.clock = pg.time.Clock()
        self.mode = "splash"
        self.prev_mode = self.mode
        self.target_speed = 1
        self.speed = 1
        self.camera = camera.Camera(self)
        self.splash_screen = ui.SplashScreen(self)
        self.level_manager = level.LevelManager(self)
        self.player = player.Player(self)
        self.enemy_manager = enemy.EnemyManager(self)
        self.particle_manager = particle.ParticleManager(self)
        self.powerup_manager = powerup.PowerUpManager(self)
        self.trap_manager = trap.TrapManager(self)

    def change_speed(self, speed):
        self.target_speed = speed

    def update(self, dt):
        ds = self.target_speed - self.speed # Delta speed
        self.speed += ds * 4 * dt # Increase the constant to increase the speed change
        dt *= self.speed # Change global game speed

        if self.mode == "splash":
            self.splash_screen.update(dt)
        if self.mode == "story":
            if self.prev_mode != self.mode:
                self.story_screen = ui.StoryScreen(self)
            self.story_screen.update(dt)
        if self.mode == "level":
            if self.prev_mode != self.mode:
                self.level_screen = ui.LevelScreen(self)
            self.level_screen.update(dt)
        if self.mode == "main":
            if self.prev_mode != self.mode:
                self.level_manager.load_level() # Load level
                self.camera.shake(200)
            self.camera.update(dt)
            self.level_manager.update(dt)
            self.player.update(dt)
            self.enemy_manager.update(dt)
            self.particle_manager.update(dt)
            self.powerup_manager.update(dt)
            self.trap_manager.update(dt)

        self.prev_mode = self.mode

    def draw(self):
        if self.mode == "splash":
            self.splash_screen.draw(self.screen)
        if self.mode == "story":
            self.story_screen.draw(self.screen)
        if self.mode == "level":
            self.level_screen.draw(self.screen)
        if self.mode == "main":
            self.level_manager.draw(self.screen)
            self.powerup_manager.draw(self.screen)
            self.player.draw(self.screen)
            self.enemy_manager.draw(self.screen)
            self.particle_manager.draw(self.screen)
            self.trap_manager.draw(self.screen)

            # Top layers
            self.level_manager.draw_lockdown_filter(self.screen)

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

            self.screen.fill(BG_COLOR)
            self.draw()
            self.window.fill(BG_COLOR)
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