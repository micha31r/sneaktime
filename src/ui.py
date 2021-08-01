import pygame as pg

from settings import *
from scripts import *

class SplashScreen:
    def __init__(self, game):
        self.game = game
        self.heading = Text(0, 0, 'Infiltrate', (255, 255, 255), 0.05, 64)
        self.subheading = Text(0, 0, 'Press space to start', (255, 255, 255), 0.05)
        self.show_subheading = False
        self.delay = 2

    def update(self, dt):
        self.heading.update(dt)
        # Align text to the center of the screen
        x, y, _, _ = self.heading.text_obj.get_rect(center=center(0, 0, *self.game.window.get_size()))
        self.heading.pos = pg.Vector2(x, y)

        if self.show_subheading:
            self.subheading.update(dt)
            # Align text to the center of the screen
            x, y, _, _ = self.subheading.text_obj.get_rect(center=center(0, 0, *self.game.window.get_size()))
            self.subheading.pos = pg.Vector2(x, y + self.heading.ch)

        if not self.show_subheading and self.heading.index == len(self.heading.text):
            self.delay -= dt
            if self.delay < 0:
                self.show_subheading = True
                self.heading.focus = False

        if self.show_subheading and self.subheading.index == len(self.subheading.text):
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE]:
                self.game.mode = "main"

    def draw(self, screen):
        self.heading.draw(screen)
        if self.show_subheading:
            self.subheading.draw(screen)

