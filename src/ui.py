
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

import pygame as pg
import theme
from settings import *
from scripts import *

class Text:
    def __init__(self, x, y, text, color, interval, size=16, direction=1, typing_effect=True, delay=0):
        self.pos = pg.Vector2(x, y)
        self.text = text
        self.color = color
        self.delay = delay
        self.interval = interval
        self.timer = interval
        self.direction = direction
        self.index = 0 if direction == 1 else len(self.text) - 1
        self.font = pg.font.Font(rs_dir + "/fonts/RobotoMonoMedium.ttf", size)
        self.focus = True
        self.cursor = False
        self.cursor_timer = 0.4
        
        if not typing_effect:
            self.index = len(self.text)
            self.focus = False

        _, _, self.cw, self.ch = self.font.render("0", True, self.color).get_rect()
        self.text_obj = self.font.render(self.text[:self.index], True, self.color)

    def update(self, dt):
        typing = False

        if self.delay > 0:
            self.delay -= dt
        else:
            self.timer -= dt
            if self.timer < 0:
                if (self.direction == 1 and self.index < len(self.text)) or (self.direction == -1 and self.index > 0):
                    # Only play sound for every 2 characters typed
                    if self.index % 2 == 0:
                        sound_effects["click"].play()
                    self.index += self.direction
                    self.timer = self.interval
                    self.text_obj = self.font.render(self.text[:self.index], True, self.color)
                    # Show cursor while typing
                    self.cursor = True
                    typing = True

        # Blink cursor
        if self.focus:
            if not typing:
                self.cursor_timer -= dt
                if self.cursor_timer < 0:
                    self.cursor_timer = 0.5
                    if self.cursor:
                        self.cursor = False
                    else:
                        self.cursor = True
        else:
            self.cursor = False

    def draw(self, screen):
        if self.cursor:
            pg.draw.rect(screen, self.color, (self.pos.x + self.cw * self.index, self.pos.y, self.cw, self.ch))
        screen.blit(self.text_obj, self.pos)
        

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
                # Load from any previous states or continue to the story screen
                if not self.game.load():
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
            Text(0, 0, 'Story:', self.game.get_color("primary"), 0.05, delay=2),
            Text(0, 0, 'The bad guys are building something sinister,', self.game.get_color("text"), 0.05),
            Text(0, 0, 'you need to sneak into their base and destroy', self.game.get_color("text"), 0.05),
            Text(0, 0, 'whatever technology they are hiding.', self.game.get_color("text"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Controls:', self.game.get_color("primary"), 0.05),
            Text(0, 0, 'Arrow keys to move.', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Hold down SPACE to aim,', self.game.get_color("text"), 0.05),
            Text(0, 0, 'use left and right arrows to adjust the angle,', self.game.get_color("text"), 0.05),
            Text(0, 0, 'then release SPACE to shoot.', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Hold down "e" to view mission progress.', self.game.get_color("text"), 0.05),
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
                    self.game.mode = "select"
                    self.game.speed = 1
                    self.game.select_screen = SelectScreen(self.game)
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


class SelectScreen:
    def __init__(self, game, typing_effect=True):
        self.game = game
        self.button_img = pg.image.load(rs_dir + "/button.png").convert_alpha()
        self.button_pressed_img = pg.image.load(rs_dir + "/button_pressed.png").convert_alpha()
        self.heading = Text(0, 0, 'Select Level:', self.game.get_color("primary"), 0.05, delay=2, typing_effect=typing_effect)
        self.numbers = []
        self.font = pg.font.Font(rs_dir + "/fonts/RobotoMonoMedium.ttf", 16)
        _, _, self.cw, self.ch = self.font.render("0", True, (0, 0, 0)).get_rect()
        self.button_width = 100
        self.button_height = 100
        self.block_width = self.button_width * 4
        self.block_height = self.button_height * 3 + 50
        self.button_timer = 0.05
        self.visible_buttons = 0
        self.selected_button = self.game.level_manager.current_level
        self.key_down = False
        self.game.camera.reset()

    def update(self, dt):
        if self.heading.index == len(self.heading.text):
            if self.visible_buttons < len(self.game.level_manager.levels):
                self.button_timer -= dt
                if self.button_timer < 0:
                    self.visible_buttons += 1
                    self.button_timer = 0.05
            else:
                keys = pg.key.get_pressed()
                if keys[pg.K_LEFT]:
                    if not self.key_down and self.selected_button > 0:
                        self.selected_button -= 1
                    self.key_down = 1
                elif keys[pg.K_RIGHT]:
                    if not self.key_down:
                        self.selected_button += 1
                        max_level = self.game.level_manager.unlocked_level
                        if self.selected_button > max_level: 
                            self.selected_button = max_level
                    self.key_down = 2
                elif keys[pg.K_SPACE]:
                    sound_effects["confirm"].play()
                    self.game.mode = "level"
                    # Reset tutorial if level 0 is selected
                    if self.selected_button == 0 and self.game.level_manager.first_level or self.game.level_manager.current_level != 0:
                        self.game.player.completed_tutorial = False
                        self.game.tutorial_manager.reset()
                    else:
                        self.game.player.completed_tutorial = True
                    self.game.level_manager.switch(self.selected_button)
                    self.game.level_screen = LevelScreen(self.game)
                else:
                    self.key_down = 0

        self.heading.update(dt)
        # Align text to the center of the screen
        _, wh = self.game.window.get_size()
        x, _, _, _ = self.heading.text_obj.get_rect(center=center(0, 0, *self.game.window.get_size()))
        self.heading.pos = pg.Vector2(x, (wh - self.block_height) / 2)

    def draw(self, screen):
        self.heading.draw(screen)

        ww, wh = self.game.window.get_size()
        self.start_x = (ww - self.block_width) / 2
        self.start_y = (wh - self.block_height) / 2 + 50

        # Draw buttons after all buttons are rendered
        if self.visible_buttons > len(self.game.level_manager.levels) - 1:
            iw, ih = self.button_img.get_size()
            left_img = self.button_img
            right_img = self.button_img
            if self.key_down == 1:
                left_img = self.button_pressed_img
            elif self.key_down == 2:
                right_img = self.button_pressed_img
            screen.blit(left_img, (self.start_x - 64 - iw/2, (wh - ih)/2))
            screen.blit(right_img, (self.start_x + 64 + self.block_width - iw/2, (wh - ih)/2))

        x = 0
        y = 0
        for i in range(10):
            if i < self.visible_buttons:
                gap = 20
                pos = pg.Vector2(self.start_x + self.button_width * x, self.start_y + self.button_height * y)
                bg_color = (0, 0, 0)
                color = (0, 0, 0)
                stroke = 1
                if self.game.level_manager.level_unlocked(i):
                    # bg_color = theme.THEMES[self.game.level_manager.current_level_obj(i)["theme"]]["primary"]
                    # if brightness(*bg_color) < 150:
                    color = (255, 255, 255)
                    stroke = 0
                # Draw rect and create text object
                obj = self.font.render(str(i), True, color)
                if self.selected_button == i:
                    gap = 10
                pg.draw.rect(screen, bg_color, (pos.x + gap, pos.y + gap, self.button_width - 2*gap, self.button_height - 2*gap), stroke, 20, 20, 20, 20)
                # Draw number
                offset_pos = pg.Vector2((self.button_width - self.cw) / 2, (self.button_height - self.ch) / 2)
                screen.blit(obj, pos + offset_pos)
                x += 1
                if x > 3:
                    y += 1
                    x = 0


class CompleteScreen(StoryScreen):
    def __init__(self, game):
        super().__init__(game)
        # Add stats together
        stats = {}
        # Ignore the first level because its a tutorial
        for data in self.game.level_manager.level_stats[1:]:
            if data:
                for k, v in data.items():
                    if k in stats: stats[k] += v
                    else: stats[k] = v
        self.lines = [
            Text(0, 0, 'Congratulations, you have completed your mission', self.game.get_color("text"), 0.05, delay=2),
            Text(0, 0, 'and destroyed the bad guys\' technology!', self.game.get_color("text"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Mission Report:', self.game.get_color("primary"), 0.05),
            Text(0, 0, f'Time: {round(stats["gameplay_timer"], 2)}s', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Death Count: {stats["death_count"]}', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Enemy Killed: {stats["kill_count"]}', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Lockdown Triggered: {stats["lockdown_count"]}', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Powerup Used: {stats["powerup_count"]}', self.game.get_color("text"), 0.05),
            Text(0, 0, f'Bullet Used: {stats["bullet_count"]}', self.game.get_color("text"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Thank you for playing.', self.game.get_color("text"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Copyright 2021 Michael Ren', self.game.get_color("primary"), 0.05),
            Text(0, 0, '', self.game.get_color("text"), 0.05),
            Text(0, 0, 'Audio by:', self.game.get_color("primary"), 0.05),
            Text(0, 0, 'Kenney Audio Assets', self.game.get_color("primary"), 0.05),
            Text(0, 0, 'Shapeforms Audio Assets', self.game.get_color("primary"), 0.05),
            Text(0, 0, 'Mixkit Audio Assets', self.game.get_color("primary"), 0.05),
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
        level = self.game.level_manager.current_level
        if level > 0:
            self.text = Text(0, 0, 'Sector ' + str(level), self.game.get_color("text"), 0.05, delay=2)
        else:
            self.text = Text(0, 0, "Tutorial", self.game.get_color("text"), 0.05, delay=2)
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
        if primary_brightness < 150:
            color = (255, 255, 255)
        self.text = Text(0, 0, text, color, 0.02, typing_effect=typing_effect)
        self.retract = retract
        self.retract_delay = delay
        self.render_height = 0
        self.transition_speed = 4
        self.complete = False
        self.set_target_y()

    def set_target_y(self, y=None):
        self.target_y = y or self.text.ch + self.margin * 2

    def is_expired(self):
        return self.complete

    def update(self, dt):
        dt /= self.game.speed or 1
        dy = self.target_y - self.render_height
        self.render_height += dy * self.transition_speed * dt
        if dy < 0.01:
            self.text.update(dt)
            if self.retract:
                if self.text.index == len(self.text.text):
                    self.retract_delay -= dt
                    if self.retract_delay < 0:
                        self.set_target_y(-2)
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




