import sys, json, math
import pygame as pg
from os import path
from collision import *


####################
# Setup
####################


BASE_DIR = path.dirname(__file__)

# Settings
W_SIZE = W_WIDTH, W_HEIGHT = 640, 480
MODE = "main"
BG_COLOR = (200,200,200)
rs_dir = path.join(BASE_DIR, "resources")

# Initialize pygame
pg.init()
pg.display.set_caption("Gravity")
window = pg.display.set_mode(W_SIZE, pg.RESIZABLE)
screen = pg.Surface((640*2,480*2))
clock = pg.time.Clock()
font = pg.font.Font(rs_dir + "/m6x11.ttf", 64)


####################
# Scripts
####################


def center(w1, h1, w2, h2):
    return ((w2-w1)/2, (h2-h1)/2)


####################
# Main Code
####################


class Camera:
    def __init__(self):
        self.pos = pg.Vector2()
        self.scale = pg.Vector2(1,1)
        self.vel = pg.Vector2()
        self.margin = 120
        self.madx = 400
        self.friction = 0.99
        self.do_track = True
        self.multiplier = 4

    def track(self, rect):
        if self.do_track:
            # Horzontal tracking
            if rect[0] < self.pos.x + self.margin:
                self.vel.x = (rect[0] - (self.pos.x + self.margin)) * self.multiplier
            if rect[0] + rect[2] > self.pos.x + self.width - self.margin:
                self.vel.x = ((rect[0] + rect[2]) - (self.pos.x + self.width - self.margin)) * self.multiplier

            # Verticle tracking
            if rect[1] < self.pos.y + self.margin:
                self.vel.y = (rect[1] - (self.pos.y + self.margin)) * self.multiplier
            if rect[1] + rect[3] > self.pos.y + self.height - self.margin:
                self.vel.y = ((rect[1] + rect[3]) - (self.pos.y + self.height - self.margin)) * self.multiplier

        # Set max velocity
        self.vel.x = self.vel.x if self.vel.x > -self.madx else -self.madx
        self.vel.x = self.vel.x if self.vel.x < self.madx else self.madx
        self.vel.y = self.vel.y if self.vel.y < self.madx else self.madx
        self.vel.y = self.vel.y if self.vel.y < self.madx else self.madx

    def update(self, dt, window_size):
        self.width = window_size[0] / self.scale.x
        self.height = window_size[1] / self.scale.x

        # Move camera
        self.pos.x += self.vel.x * dt
        self.pos.y += self.vel.y * dt

        # Decrease velocity
        self.vel.x *= self.friction
        self.vel.y *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel.x) < 0.01:
            self.vel.x = 0
        if abs(self.vel.y) < 0.01:
            self.vel.y = 0


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


class TiledMap:
    def __init__(self):
        self.load_tilemap()
        self.load_tileset()
        self.load_polygons()

    def load_tilemap(self):
        f = open(rs_dir + "/tilemap.json")
        self.data = json.load(f)

    def load_tileset(self):
        img = pg.image.load(rs_dir + "/tilesheet.png")
        img_width, img_height = img.get_size()
        tile_width, tile_height = self.data["tilewidth"], self.data["tileheight"]
        self.tileset = []
        for tile_y in range(math.floor(img_height / tile_height)):
            img_y = tile_y * tile_height
            for tile_x in range(math.floor(img_width / tile_width)):
                img_x = tile_x * tile_width
                rect = (img_x, img_y, tile_width, tile_height)
                self.tileset.append(img.subsurface(rect))

    def rect_collide(self, rect, target_layer_name=None):
        x1 = rect[0]
        y1 = rect[1]
        w1 = rect[2]
        h1 = rect[3]
        for layer in self.data["layers"]:
            if layer["type"] == "objectgroup":
                if not target_layer_name or target_layer_name == layer["name"]:
                    for obj in layer["objects"]:
                        # Check for intersection
                        x2 = obj["x"]
                        y2 = obj["y"]
                        w2 = obj["width"]
                        h2 = obj["height"]
                        if ((x1 < x2 and x1 + w1 > x2) or \
                            (x1 < x2 + w2 and x1 + w1 > x2 + w2) or \
                            (x1 > x2 and x1 + w1 < x2 + w2)) and \
                            ((y1 < y2 and y1 + h1 > y2) or \
                            (y1 < y2 + h2 and y1 + h1 > y2 + h2) or \
                            (y1 > y2 and y1 + h1 < y2 + h2)):
                            return True

    # All polygons must be convex
    def load_polygons(self):
        v = Vector
        self.polygons = {}
        for layer in self.data["layers"]:
            if layer["type"] == "objectgroup":
                polys = []
                for obj in layer["objects"]:
                    if "polygon" in obj:
                        points = []
                        for p in obj["polygon"]:
                            points.append(v(p["x"], p["y"]))
                        polys.append(Poly(v(obj["x"],obj["y"]), points))
                if polys:
                    self.polygons[layer["name"]] = polys


    def poly_collide(self, rect, target_layer_name=None):
        v = Vector
        x1 = rect[0] + 32
        y1 = rect[1] + 32
        # w1 = rect[2]
        # h1 = rect[3]
        p1 = Circle(v(x1,y1), 32)
        # Must capture all collisions for r.overlap_v to work,
        # otherwise 'a' will tunnel into 'b' while responding collision with 'c'
        all_collisions = []
        for layer_name, items in self.polygons.items():
            if not target_layer_name or target_layer_name == layer_name:
                for p2 in items:
                    # Collision responses are only supported for convex polygons
                    r = Response()
                    if collide(p1, p2, response=r):
                        # Calculate the collision angle
                        # angle = round(math.atan2(*r.overlap_n)*180/math.pi)
                        all_collisions.append(r.overlap_v)
        return all_collisions or None

    def update(self):
        pass

    def draw(self):
        data = self.data
        tilewidth = data["tilewidth"]
        tileheight = data["tileheight"]
        for layer in data["layers"]:
            if layer["visible"] == True and layer["type"] == "tilelayer":
                for chunk in layer["chunks"]:
                    cw = chunk["width"]
                    ch = chunk["height"]
                    cx = chunk["x"]
                    cy = chunk["y"]
                    tx = 0
                    ty = 0
                    for tile_id in chunk["data"]:
                        render_x = (cx + tx) * tilewidth 
                        render_y = (cy + ty) * tileheight
                        # means there is no tile
                        if tile_id != 0:
                            screen.blit(self.tileset[tile_id-1], (render_x, render_y, tilewidth, tileheight))
                        tx += 1
                        if tx == cw:
                            tx = 0
                            ty += 1

class ParticleManager:
    def __init__(self):
        self.particles = []

    def add(self, p):
        self.particles.append(p)

    def update(self, dt):
        for i, p in reversed(list(enumerate(self.particles))):
            p.update(dt)
            if p.can_be_terminated() == True:
                del self.particles[i]

    def draw(self):
        for p in self.particles:
            p.draw()

class Bullet:
    def __init__(self, x, y, angle):
        self.pos = pg.Vector2(x,y)
        self.vel = pg.Vector2(800,800)
        self.angle = angle
        self.lifespan_counter = 0

    def update(self, dt):
        rad = math.radians(self.angle)
        self.pos.x += math.cos(rad) * self.vel.x * dt
        self.pos.y += math.sin(rad) * self.vel.y * dt
        self.lifespan_counter += 1

    def can_be_terminated(self):
        if self.lifespan_counter > 256:
            return True

    def draw(self):
        pg.draw.circle(screen, (0,0,0), self.pos, 8)

class Player:
    def __init__(self):
        self.pos = pg.Vector2()
        self.vel = pg.Vector2()
        self.madx = 260
        self.friction = 0.8
        self.mode = "move"

        self.can_shoot = True
        self.shoot_counter = 0
        self.angle = 0

        # Sprites & Animation
        self.img_path = "/characters/circle.png"
        self.frame_width, self.frame_height = 64, 64
        self.frame_sets = {
            "idle": {
                "frames": [0]
            },
            "move": {
                "frames": [0]
            },
        }
        self.current_frame_set = "idle"
        self.current_frame_index = 0
        self.animation_counter = 0
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

    def shoot(self):
        if self.can_shoot:
            game.particle_manager.add(Bullet(
                self.pos.x + self.frame_width/2,
                self.pos.y + self.frame_height/2,
                self.angle
            ))
            self.can_shoot = False

    def update(self, dt):
        # Update animation frames
        self.animation_counter += 1
        if self.animation_counter > 5:
            max_frame = len(self.frame_sets[self.current_frame_set]["frames"])-1
            if self.current_frame_index < max_frame:
                self.current_frame_index += 1
            else:
                self.current_frame_index = 0
            self.animation_counter = 0

        # Update shoot counter
        if not self.can_shoot:
            self.shoot_counter += 1
            if self.shoot_counter > 60:
                self.can_shoot = True
                self.shoot_counter = 0

        # Set initial velocities on keypress
        keys = pg.key.get_pressed()

        if self.can_shoot:
            if keys[pg.K_SPACE]:
                self.mode = "aim"
            elif self.mode == "aim": # If key is just released and the control mode hasn't changed
                self.shoot()
                self.mode = "move"

        if self.mode == "move":
            if keys[pg.K_LEFT]:
                self.vel.x = -self.madx
            elif keys[pg.K_RIGHT]:
                self.vel.x = self.madx
            if keys[pg.K_UP]:
                self.vel.y = -self.madx
            elif keys[pg.K_DOWN]:
                self.vel.y = self.madx
        elif self.mode == "aim":
            if keys[pg.K_LEFT]:
                self.angle -= 200 * dt
            elif keys[pg.K_RIGHT]:
                self.angle += 200 * dt
            # Limit angle
            if self.angle < 0:
                self.angle = 360 + self.angle
            if self.angle > 360:
                self.angle = self.angle - 360

        # Move player
        dx = self.vel.x * dt
        dy = self.vel.y * dt

        # Collision
        self.pos.x += dx
        self.pos.y += dy
        all_collisions = game.tilemap.poly_collide((self.pos.x, self.pos.y, self.frame_width, self.frame_height))
        if all_collisions:
            for c in all_collisions:
                self.pos.x -= c.x
                self.pos.y -= c.y
                # pass
            self.vel.x = 0
            self.vel.y = 0

        # Decrease velocity
        self.vel.x *= self.friction
        self.vel.y *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel.x) < 0.05:
            self.vel.x = 0
        if abs(self.vel.y) < 0.05:
            self.vel.y = 0

        # Change animation
        if max(abs(self.vel.x), abs(self.vel.y)) > 1:
            if self.current_frame_set != "move":
                self.current_frame_index = 0
                self.current_frame_set = "move"
        else:
            if self.current_frame_set != "idle":
                self.current_frame_index = 0
                self.current_frame_set = "idle"

        camera.track((self.pos.x, self.pos.y, self.frame_width, self.frame_height))

    def draw(self):
        # Draw self
        img = self.frames[self.frame_sets[self.current_frame_set]["frames"][self.current_frame_index]]
        screen.blit(img, self.pos)
        
        if self.mode == "aim":
            # Draw aiming lines
            rad = math.radians(self.angle)
            start_pos = pg.Vector2(self.pos.x + self.frame_width/2, self.pos.y + self.frame_height/2)
            end_pos = pg.Vector2(start_pos.x + math.cos(rad)*500, start_pos.y + math.sin(rad)*500)
            pg.draw.line(screen, (0,0,0), start_pos, end_pos)

class Game:
    def __init__(self):
        self.splash_screen = SplashScreen()
        self.prev_mode = MODE
        self.tilemap = TiledMap()
        self.player = Player()
        self.particle_manager = ParticleManager()

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
            self.particle_manager.update(dt)
        self.prev_mode = MODE

    def draw(self):
        if MODE == "splash":
            self.splash_screen.draw()
        if MODE == "main":
            self.tilemap.draw()
            self.player.draw()
            self.particle_manager.draw()

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
    
    dt = clock.tick(60) / 1000
    window_size = window.get_rect().size
    screen_size = screen.get_rect().size

    camera.update(dt, window_size)
    game.update(dt)
    screen.fill(BG_COLOR)
    game.draw()
    # Render main surface after scaling it by the scale factor
    window.fill(BG_COLOR)
    window.blit(
        pg.transform.scale(screen, (int(screen_size[0]*camera.scale.x), int(screen_size[1]*camera.scale.x))),
        (0,0),
        (camera.pos.x*camera.scale.x, camera.pos.y*camera.scale.x, window.get_width(), window.get_height())
    )
    pg.display.flip()