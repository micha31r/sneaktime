import pygame as pg

from settings import *
from scripts import *

class SplashScreen:
    def __init__(self, game):
        self.game = game
        self.heading = Text(0, 0, 'Break In', (128, 35, 255), 0.05, 64)
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
                self.game.story_screen = StoryScreen(self.game)

    def draw(self, screen):
        self.heading.draw(screen)
        if self.show_subheading:
            self.subheading.draw(screen)


class StoryScreen:
    def __init__(self, game):
        self.game = game
        self.lines = [
            Text(0, 0, 'Mission:', (128, 35, 255), 0.05),
            Text(0, 0, 'The bad guys have stole the source code of the world\'s', (255, 255, 255), 0.05),
            Text(0, 0, 'most powerful AI. You need to break into their super', (255, 255, 255), 0.05),
            Text(0, 0, 'secure facility and erase the data ASAP.', (255, 255, 255), 0.05),
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
                    self.game.level_screen = LevelScreen(self.game)
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
        self.text = Text(0, 0, 'Sector ' + str(self.game.level_manager.current_level), (255, 255, 255), 0.05)
        self.delay = 4
        # Reset camera pos
        self.game.camera.reset()

    def update(self, dt):
        if self.text.index == len(self.text.text):
            self.delay -= dt
            if self.delay < 0:
                self.game.mode = "main"
                self.game.level_manager.load_level() # Load level
                self.game.camera.shake(200)
        self.text.update(dt)

    def draw(self, screen):
        # Align text center horizontally
        x, y, _, _ = self.text.text_obj.get_rect(center=center(0, 0, *self.game.window.get_size()))
        self.text.pos = pg.Vector2(x, y)
        self.text.draw(screen)


class InterfaceManager:
    def __init__(self, game):
        self.game = game
        self.items = []

    def add(self, item):
        self.items.append(item)
        return self.items[-1]

    def message(self, text, retract=True, delay=2, typing_effect=True):
        return self.add(PopUpMessage(self.game, text, retract, delay, typing_effect=typing_effect))

    def update(self, dt):
        for i, item in reversed(list(enumerate(self.items))):
            item.update(dt)
            if item.is_expired():
                del self.items[i]

    def reset(self):
        self.items = []

    def draw(self, screen):
        for item in self.items:
            item.draw(screen)


class PopUpMessage:
    def __init__(self, game, text, retract=True, delay=2, typing_effect=True):
        self.game = game
        self.margin = 4
        self.text = Text(0, 0, text, (255, 255, 255), 0.02, typing_effect=typing_effect)
        self.retract = retract
        self.retract_delay = delay
        self.render_height = 0
        self.transition_speed = 4
        self.target_y = self.text.ch + self.margin * 2
        self.complete = False

    def is_expired(self):
        return self.complete

    def update(self, dt):
        dt /= self.game.speed
        dy = self.target_y - self.render_height
        self.render_height += dy * self.transition_speed * dt
        if dy < 0.01:
            self.text.update(dt)
            if self.retract:
                if self.text.index == len(self.text.text):
                    self.retract_delay -= dt
                    if self.retract_delay < 0:
                        self.target_y = -2
            # Mark as complete if already retracted
            if self.render_height < 0:
                self.complete = True
        _, wh = self.game.window.get_size()
        self.text.pos.x = self.game.camera.pos.x + self.margin + 4
        self.text.pos.y = self.game.camera.pos.y + wh - self.render_height + self.margin

    def draw(self, screen):
        ww, wh = self.game.window.get_size()
        pg.draw.rect(screen, (128, 35, 255), (self.game.camera.pos.x, self.game.camera.pos.y + wh - self.render_height, ww, self.render_height + 5))
        self.text.draw(screen)




