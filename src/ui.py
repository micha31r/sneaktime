import pygame as pg

from settings import *
from scripts import *

class SplashScreen:
    def __init__(self, game):
        self.game = game
        self.heading = Text(0, 0, 'BreakIn()', (128, 35, 255), 0.05, 64)
        self.subheading = Text(0, 0, 'Press SPACE to start', (255, 255, 255), 0.05)
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
                self.game.mode = "story"

    def draw(self, screen):
        self.heading.draw(screen)
        if self.show_subheading:
            self.subheading.draw(screen)

class StoryScreen:
    def __init__(self, game):
        self.game = game
        self.lines = [
            Text(0, 0, 'Mission:', (128, 35, 255), 0.05),
            Text(0, 0, 'Break into the PI base and destroy their experiment,', (255, 255, 255), 0.05),
            Text(0, 0, 'time is running out...', (255, 255, 255), 0.05),
            Text(0, 0, '', (255, 255, 255), 0.05),
            Text(0, 0, 'Controls:', (128, 35, 255), 0.05),
            Text(0, 0, 'Arrow keys to move.', (255, 255, 255), 0.05),
            Text(0, 0, 'Hold down SPACE to enter aim,', (255, 255, 255), 0.05),
            Text(0, 0, 'use left and right arrows to adjust angle,', (255, 255, 255), 0.05),
            Text(0, 0, 'release SPACE to shoot.', (255, 255, 255), 0.05),
            Text(0, 0, '', (255, 255, 255), 0.05),
            Text(0, 0, 'Press SPACE to begin ', (255, 255, 255), 0.05),
        ]
        self.line_index = 0
        self.block_height = self.lines[0].ch * len(self.lines)
        self.delay = 1

    def update(self, dt):
        keys = pg.key.get_pressed()
        # Speed up text
        if keys[pg.K_SPACE]: self.game.speed = 4
        else: self.game.speed = 1
        
        t = self.lines[self.line_index]
        if t.index == len(t.text):
            self.delay -= dt
            if self.delay < 0 and self.line_index < len(self.lines)-1:
                self.delay = 1
                self.line_index += 1
                t.focus = False
            if self.line_index == len(self.lines)-1:
                if keys[pg.K_SPACE]:
                    self.game.mode = "level"
                    self.game.speed = 1
        t.update(dt)


    def draw(self, screen):
        _, wh = self.game.window.get_size()
        self.start_y = (wh - self.block_height) / 2

        for i, t in enumerate(self.lines):
            # Align text center horizontally
            x, _, _, _ = t.text_obj.get_rect(center=center(0, 0, *self.game.window.get_size()))
            t.pos = pg.Vector2(x, self.start_y + t.ch * i)
            t.draw(screen)

class LevelScreen:
    def __init__(self, game):
        self.game = game
        self.text = Text(0, 0, 'sector ' + str(self.game.level_manager.current_level), (255, 255, 255), 0.05)
        self.delay = 4

    def update(self, dt):
        if self.text.index == len(self.text.text):
            self.delay -= dt
            if self.delay < 0:
                self.game.mode = "main"
        self.text.update(dt)

    def draw(self, screen):
        # Align text center horizontally
        x, y, _, _ = self.text.text_obj.get_rect(center=center(0, 0, *self.game.window.get_size()))
        self.text.pos = pg.Vector2(x, y)
        self.text.draw(screen)

