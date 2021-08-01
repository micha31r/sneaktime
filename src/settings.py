import pygame as pg
from os import path

pg.init()

BASE_DIR = path.dirname(__file__)
WINDOW_SIZE = W_WIDTH, W_HEIGHT = 640, 480
WORLD_SIZE = (640*3, 480*3)
BG_COLOR = (0, 0, 0)

rs_dir = path.join(BASE_DIR, "resources")
# font16 = pg.font.Font(rs_dir + "/fonts/RobotoMonoMedium.ttf", 16)