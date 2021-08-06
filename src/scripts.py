import math
import pygame as pg
from collision import *

from settings import *

def center(x, y, w, h, default=True):
    if not default:
        return Vector(x+w/2, y+h/2)
    return pg.Vector2(x+w/2, y+h/2)

# Draw n sided regular polygons
# https://stackoverflow.com/questions/29064259/drawing-pentagon-hexagon-in-pygame
def draw_ngon(Surface, color, n, radius, position, angle=0):
    pi2 = math.pi * 2
    return pg.draw.lines(Surface, color, True, [(math.cos(i / n * pi2 + angle) * radius + position[0], math.sin(i / n * pi2 + angle) * radius + position[1]) for i in range(0, n)], 2)

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

