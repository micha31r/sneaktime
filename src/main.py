import sys, json, math
import pygame as pg
from os import path
from settings import *
from utils import *

pg.init()
pg.display.set_caption("Top Down Game Template")
window = pg.display.set_mode(W_SIZE, pg.RESIZABLE)
screen = pg.Surface(W_SIZE)
clock = pg.time.Clock()

rs_dir = path.join(BASE_DIR, "resources")
font = pg.font.Font(rs_dir + "/m6x11.ttf", 64)

class Camera:
    def __init__(self):
        self.pos = self.x, self.y = [0,0]
        self.scale = self.scale_x, self.scale_y = 2, 2
        self.vel = [0,0]
        self.margin = 80
        self.max_vel = 50
        self.friction = 0.99
        self.do_track = True

    def track(self, rect):
        if self.do_track:
            # Horzontal tracking
            if rect[0] < self.x + self.margin:
                self.vel[0] = rect[0] - (self.x + self.margin)
            if rect[0] + rect[2] > self.x + self.width - self.margin:
                self.vel[0] = (rect[0] + rect[2]) - (self.x + self.width - self.margin)

            # Verticle tracking
            if rect[1] < self.y + self.margin:
                self.vel[1] = rect[1] - (self.y + self.margin)
            if rect[1] + rect[3] > self.y + self.height - self.margin:
                self.vel[1] = (rect[1] + rect[3]) - (self.y + self.height - self.margin)

        # Set max velocity
        self.vel[0] = self.vel[0] if self.vel[0] > -self.max_vel else -self.max_vel
        self.vel[0] = self.vel[0] if self.vel[0] < self.max_vel else self.max_vel

    def update(self, dt, window_size):
        self.width = window_size[0] / self.scale_x
        self.height = window_size[1] / self.scale_y

        # Move camera
        self.x += self.vel[0] / dt
        self.y += self.vel[1] / dt

        # Decrease velocity
        self.vel[0] *= self.friction
        self.vel[1] *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel[0]) < 0.01:
            self.vel[0] = 0
        if abs(self.vel[1]) < 0.01:
            self.vel[1] = 0


class SplashScreen:
    def __init__(self):
        self.text = font.render('Demo', True, (0,0,0))
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
            MODE = "main"

    def draw(self):
        screen.blit(self.text, center(*self.rect[2:4], *W_SIZE))

# https://bakudas.itch.io/generic-rpg-pack
class TiledMap:
    def __init__(self):
        self.load_tilemap();
        self.load_tileset();

    def load_tilemap(self):
        f = open(rs_dir + "/tilemap.json")
        self.data = json.load(f)

    def load_tileset(self):
        img = pg.image.load(rs_dir + "/tileset.png")
        img_width, img_height = img.get_size()
        tile_width, tile_height = self.data["tilewidth"], self.data["tileheight"]
        self.tileset = []
        for tile_y in range(math.floor(img_height / tile_height)):
            img_y = tile_y * tile_height
            for tile_x in range(math.floor(img_width / tile_width)):
                img_x = tile_x * tile_width
                rect = (img_x, img_y, tile_width, tile_height)
                self.tileset.append(img.subsurface(rect))

    def update(self):
        pass

    def draw(self):
        data = self.data
        tilewidth = data["tilewidth"]
        tileheight = data["tileheight"]
        for layer in data["layers"]:
            if layer["type"] == "tilelayer":
                for chunk in layer["chunks"]:
                    cw = chunk["width"]
                    ch = chunk["height"]
                    cx = chunk["x"]
                    cy = chunk["y"]
                    tx = 0
                    ty = 0
                    for tile_id in chunk["data"]:
                        render_x = (cx + tx) * tilewidth # + (0-layer["startx"] * 16)
                        render_y = (cy + ty) * tileheight # + (0-layer["starty"] * 16)
                        # means there is no tile
                        if tile_id != 0:
                            screen.blit(self.tileset[tile_id-1], (render_x, render_y, tilewidth, tileheight))
                        tx += 1
                        if tx == cw:
                            tx = 0
                            ty += 1

class Player:
    def __init__(self):
        self.pos = [0,0]
        self.vel = [0,0]
        self.max_vel = 30
        self.friction = 0.8

        # Sprites & Animation
        self.img_path = "/characters/gabe-idle-run.png"
        self.frame_width, self.frame_height = 24, 24
        self.idle_frames = [0]
        self.movement_frames = [1,2,3,4,5,6]
        self.animation_counter = 0
        self.is_idle = True
        self.current_frame_index = 0
        self.load_frames()

    def load_frames(self):
        img = pg.image.load(rs_dir + self.img_path)
        img_width, img_height = img.get_size()
        self.frames = []
        for frame_y in range(math.floor(img_height / self.frame_height)):
            img_y = frame_y * self.frame_height
            for frame_x in range(math.floor(img_width / self.frame_width)):
                img_x = frame_x * self.frame_width
                rect = (img_x, img_y, self.frame_width, self.frame_height)
                self.frames.append(img.subsurface(rect))

    def update(self, dt):
        self.animation_counter += 1 / dt
        if self.animation_counter > 1:
            if self.is_idle:
                self.current_frame_index += 1
                if self.current_frame_index > len(self.idle_frames) - 1:
                    self.current_frame_index = 0

        # Set initial velocities on keypress
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.vel[0] = -self.max_vel
        elif keys[pg.K_RIGHT]:
            self.vel[0] = self.max_vel
        if keys[pg.K_UP]:
            self.vel[1] = -self.max_vel
        elif keys[pg.K_DOWN]:
            self.vel[1] = self.max_vel

        # Move player
        self.pos[0] += self.vel[0] / dt
        self.pos[1] += self.vel[1] / dt

        # Decrease velocity
        self.vel[0] *= self.friction
        self.vel[1] *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel[0]) < 0.01:
            self.vel[0] = 0
        if abs(self.vel[1]) < 0.01:
            self.vel[1] = 0

        camera.track((self.pos[0], self.pos[1], self.frame_width, self.frame_height))

    def draw(self):
        if self.is_idle:
            img = self.frames[self.idle_frames[self.current_frame_index]]
        else:
            img = self.frames[self.movement_frames[self.current_frame_index]]
        screen.blit(img, self.pos)

class Game:
    def __init__(self):
        self.splash_screen = SplashScreen()
        self.prev_mode = MODE
        self.tilemap = TiledMap()
        self.player = Player()

    def update(self, dt):
        mode_changed = False
        if self.prev_mode != MODE:
            mode_changed = True
        if MODE == "splash":
            self.splash_screen.update(dt)
        if MODE == "menu":
            pass
        if MODE == "main":
            if mode_changed:
                self.player = Player()
            self.player.update(dt)
        self.prev_mode = MODE

    def draw(self):
        if MODE == "splash":
            self.splash_screen.draw()
        if MODE == "main":
            self.tilemap.draw()
            self.player.draw()

game = Game()
camera = Camera()

while 1:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        elif event.type == pg.VIDEORESIZE:
            w, h = event.size
            w = 640 if w < 640 else w
            h = 480 if h < 480 else h
            window = pg.display.set_mode((w, h), pg.RESIZABLE)
            screen = pg.transform.scale(screen, (w, h))
    
    dt = clock.tick(60)
    window_size = window.get_rect().size

    camera.update(dt, window_size)
    game.update(dt)
    screen.fill(BG_COLOR)
    game.draw()
    # Render main surface after scaling it by the scale factor
    window.fill(BG_COLOR)
    window.blit(
        pg.transform.scale(screen, (window_size[0]*camera.scale_x, window_size[1]*camera.scale_y)),
        (0,0),
        (camera.x*camera.scale_x, camera.y*camera.scale_y, window.get_width(), window.get_height())
    )
    pg.display.flip()