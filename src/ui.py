import pygame as pg

from settings import *
from scripts import *

class SplashScreen:
    def __init__(self, game):
        self.game = game
        self.heading = Text(0, 0, 'sneaktime', self.game.get_color("primary"), 0.05, 64, delay=2)
        self.subheading = Text(0, 0, 'Press SPACE to start', self.game.get_color("text"), 0.05)
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
                sound_effects["confirm"].play()
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
            Text(0, 0, 'Mission:', self.game.get_color("primary"), 0.05, delay=2),
            Text(0, 0, 'The bad guys are building something sinister,', self.game.get_color("text"), 0.05),
            Text(0, 0, 'you need to sneak into their base and destroy', self.game.get_color("text"), 0.05),
            Text(0, 0, 'whatever technology they are hiding.', self.game.get_color("text"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Controls:', self.game.get_color("primary"), 0.05),
            Text(0, 0, 'Arrow keys to move.', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Hold down SPACE to enter aim,', self.game.get_color("text"), 0.05),
            Text(0, 0, 'use left and right arrows to adjust angle,', self.game.get_color("text"), 0.05),
            Text(0, 0, 'then release SPACE to shoot.', self.game.get_color("text"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Press SPACE to begin', self.game.get_color("text"), 0.05),
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
            if self.line_index == len(self.lines)-1:
                if keys[pg.K_SPACE]:
                    sound_effects["confirm"].play()
                    self.game.mode = "level"
                    self.game.speed = 1
                    self.game.level_screen = LevelScreen(self.game)
            if self.delay < 0 and self.line_index < len(self.lines)-1:
                self.delay = 1
                self.line_index += 1
                t.focus = False
        t.update(dt)


    def draw(self, screen):
        _, wh = self.game.window.get_size()
        self.start_y = (wh - self.block_height) / 2

        for i, t in enumerate(self.lines):
            # Align text center horizontally
            x, _, _, _ = t.text_obj.get_rect(center=center(0, 0, *self.game.window.get_size()))
            t.pos = pg.Vector2(x, self.start_y + t.ch * i)
            t.draw(screen)


class CompleteScreen(StoryScreen):
    def __init__(self, game):
        super().__init__(game)
        self.lines = [
            Text(0, 0, 'Congratulations, you have completed your mission', self.game.get_color("text"), 0.05, delay=2),
            Text(0, 0, 'and destroyed the bad guys\' technology!', self.game.get_color("text"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Mission Report:', self.game.get_color("primary"), 0.05),
            Text(0, 0, f'Time: {round(self.game.player.gameplay_timer, 2)}s', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Death Count: {self.game.player.death_count}', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Enemy killed: {self.game.player.kill_count}', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Lockdown Triggered: {self.game.player.lockdown_count}', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Powerup Used: {self.game.player.powerup_count}', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Bullet Used: {self.game.player.bullet_count}', self.game.get_color("text"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Thank you for playing', self.game.get_color("text"), 0.05),
        ]
        self.block_height = self.lines[0].ch * len(self.lines)
        self.game.camera.reset()

    def update(self, dt):
        t = self.lines[self.line_index]
        if t.index == len(t.text):
            self.delay -= dt
            if self.delay < 0 and self.line_index < len(self.lines)-1:
                self.delay = 1
                self.line_index += 1
                t.focus = False
        t.update(dt)


class LevelScreen:
    def __init__(self, game):
        self.game = game
        self.text = Text(0, 0, 'Sector ' + str(self.game.level_manager.current_level), self.game.get_color("text"), 0.05, delay=2)
        self.delay = 4
        self.game.camera.reset()

    def update(self, dt):
        if self.text.index == len(self.text.text):
            self.delay -= dt
            if self.delay < 0:
                self.game.mode = "main"
                self.game.level_manager.load_level() # Load level
                self.game.camera.shake(200)
                sound_effects["start_level"].play()
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
        sound_effects["show_message"].play()
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
        primary_brightness = brightness(*self.game.get_color("primary"))
        color = (0, 0, 0)
        if primary_brightness < 128:
            color = (255, 255, 255)
        self.text = Text(0, 0, text, color, 0.02, typing_effect=typing_effect)
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
        pg.draw.rect(screen, self.game.get_color("primary"), (self.game.camera.pos.x, self.game.camera.pos.y + wh - self.render_height, ww, self.render_height + 5))
        self.text.draw(screen)




