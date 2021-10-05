
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

import json, math
import pygame as pg
from collision import *
from settings import *

def center(x, y, w, h, default=True):
    if not default:
        return Vector(x+w/2, y+h/2)
    return pg.Vector2(x+w/2, y+h/2)

def brightness(r, g, b):
    return (r + g + b) / 3

# Draw n sided regular polygons
# https://stackoverflow.com/questions/29064259/drawing-pentagon-hexagon-in-pygame
def draw_ngon(Surface, color, n, radius, position, angle=0):
    pi2 = math.pi * 2
    return pg.draw.lines(Surface, color, True, [(math.cos(i / n * pi2 + angle) * radius + position[0], math.sin(i / n * pi2 + angle) * radius + position[1]) for i in range(0, n)], 2)
