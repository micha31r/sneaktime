import sys
import pygame as pg
from os import path
from settings import *
from utils import *

pg.init()
pg.display.set_caption("Top Down Game Template")
screen = pg.display.set_mode(W_SIZE, pg.RESIZABLE)
clock = pg.time.Clock()

font = pg.font.Font(path.join(BASE_DIR, "resources/m6x11.ttf"), 64)

class SplashScreen:
    def __init__(self):
        self.text = font.render('Demo', True, (255,255,255))
        self.rect = self.text.get_rect()
        self.opacity = 0
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        sec = self.timer / 1000
        if sec <= 0.5:
            self.opacity += 255 / (0.5 / (dt / 1000))
            self.text.set_alpha(self.opacity)
        elif sec > 1.5 and sec <= 2.5:
            self.opacity -= 255 / (0.5 / (dt / 1000))
            self.text.set_alpha(self.opacity)
        elif sec > 3.5:
            global MODE
            MODE = "menu"

    def draw(self):
        screen.blit(self.text, center(*self.rect[2:4], *W_SIZE))

class Player:
    def __init__(self):
        ...

class Game:
    def __init__(self):
        self.rs_dir = path.join(BASE_DIR, "resources")
        self.splash_screen = SplashScreen()

    def update(self):
        dt = clock.tick(30)
        if MODE == "splash":
            self.splash_screen.update(dt)
        if MODE == "menu":
            pass
        if MODE == "main":
            pass

    def draw(self):
        if MODE == "splash":
            self.splash_screen.draw()
        if MODE == "menu":
            pass
        if MODE == "main":
            pass

game = Game()

while 1:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        elif event.type == pg.VIDEORESIZE:
            w, h = event.size
            w = 640 if w < 640 else w
            h = 480 if h < 480 else h
            screen = pg.display.set_mode((w, h), pg.RESIZABLE)
            
    game.update()
    screen.fill(BG_COLOR)
    game.draw()
    pg.display.flip()