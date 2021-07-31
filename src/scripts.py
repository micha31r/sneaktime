import pygame as pg

def center(x, y, w, h, default=True):
    if not default:
        return Vector(x+w/2, y+h/2)
    return pg.Vector2(x+w/2, y+h/2)