import sys, json, math, random
import pygame as pg
from os import path
from collision import *


####################
# Setup
####################


BASE_DIR = path.dirname(__file__)

# Settings
WINDOW_SIZE = W_WIDTH, W_HEIGHT = 640, 480
WORLD_SIZE = (640*3, 480*3)
MODE = "main"
BG_COLOR = (0, 0, 0)
rs_dir = path.join(BASE_DIR, "resources")

# Initialize pygame
pg.init()
pg.display.set_caption("Infiltrate")
window = pg.display.set_mode(WINDOW_SIZE, pg.RESIZABLE)
screen = pg.Surface(WORLD_SIZE)
clock = pg.time.Clock()
font = pg.font.Font(rs_dir + "/m6x11.ttf", 64)


####################
# Scripts
####################


def center(x, y, w, h, default=True):
    if not default:
        return Vector(x+w/2, y+h/2)
    return pg.Vector2(x+w/2, y+h/2)


####################
# Main Code
####################


class Camera:
    def __init__(self):
        self.pos = pg.Vector2()
        self.scale = pg.Vector2(1, 1)
        self.vel = pg.Vector2()
        self.margin = 200
        self.max_vel = 400
        self.friction = 0.8
        self.do_track = True
        self.multiplier = 4

    def track(self, rect):
        if self.do_track:
            # Horzontal tracking
            a = self.pos.x + self.margin
            if rect[0] < a:
                self.vel.x = (rect[0] - a) * self.multiplier
            b = self.pos.x + self.width - self.margin
            if rect[0] + rect[2] > b:
                self.vel.x = ((rect[0] + rect[2]) - b) * self.multiplier

            # Verticle tracking
            c = self.pos.y + self.margin
            if rect[1] < c:
                self.vel.y = (rect[1] - c) * self.multiplier
            d = self.pos.y + self.height - self.margin
            if rect[1] + rect[3] > d:
                self.vel.y = ((rect[1] + rect[3]) - d) * self.multiplier

        # Set max velocity
        self.vel.x = self.vel.x if self.vel.x > -self.max_vel else -self.max_vel
        self.vel.x = self.vel.x if self.vel.x < self.max_vel else self.max_vel
        self.vel.y = self.vel.y if self.vel.y < self.max_vel else self.max_vel
        self.vel.y = self.vel.y if self.vel.y < self.max_vel else self.max_vel

    def update(self, dt, window_size):
        self.width = window_size[0] / self.scale.x
        self.height = window_size[1] / self.scale.x

        # Move camera
        self.pos += self.vel * dt

        # Limit position
        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x + window_size[0] > WORLD_SIZE[0]:
            self.pos.x = WORLD_SIZE[0] - window_size[0]
        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y + window_size[1] > WORLD_SIZE[1]:
            self.pos.y = WORLD_SIZE[1] - window_size[1]

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
        self.text = font.render('Demo', True, (0, 0, 0))
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
        screen.blit(self.text, (0,0))


class TiledMap:
    def __init__(self, path):
        self.spawner_tiles = {
            "player": 41, 
            "enemy": 52, 
        }

        self.load_tilemap(path)
        self.load_tileset()
        self.load_polygons()
        self.load_tiles()

    def load_tilemap(self, path):
        f = open(rs_dir + path)
        self.data = json.load(f)

    def load_tileset(self):
        img = pg.image.load(rs_dir + "/tilesheet.png").convert_alpha()
        img_width, img_height = img.get_size()
        tile_width, tile_height = self.data["tilewidth"], self.data["tileheight"]
        self.tileset = []
        for tile_y in range(math.floor(img_height / tile_height)):
            img_y = tile_y * tile_height
            for tile_x in range(math.floor(img_width / tile_width)):
                img_x = tile_x * tile_width
                rect = (img_x, img_y, tile_width, tile_height)
                self.tileset.append(img.subsurface(rect))

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
                        polys.append(Poly(v(obj["x"], obj["y"]), points))
                if polys:
                    self.polygons[layer["name"]] = polys

    def load_tiles(self):
        self.spawners = {}
        self.tiles = []
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
                        render_x = (cx + tx) * tilewidth 
                        render_y = (cy + ty) * tileheight
                        # means there is no tile
                        if tile_id != 0:
                            rect = (render_x, render_y, tilewidth, tileheight)
                            if layer["visible"]:
                                self.tiles.append({
                                    "img": self.tileset[tile_id-1], 
                                    "rect": rect
                                })
                            else:
                                for k, v in self.spawner_tiles.items():
                                    if tile_id == v:
                                        if k not in self.spawners:
                                            self.spawners[k] = []
                                        self.spawners[k].append(rect)
                        tx += 1
                        if tx == cw:
                            tx = 0
                            ty += 1

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

    def poly_collide(self, p1, target_layer_name=None, capture_all=False):
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
                        if capture_all:
                            all_collisions.append(r.overlap_v)
                        else:
                            return r.overlap_v
        return all_collisions

    def draw(self):
        for t in self.tiles:
            rect = t["rect"]
            # Only render tile if it's within the viewport
            if (rect[0] + rect[2] > camera.pos.x and rect[0] < camera.pos.x + WORLD_SIZE[0]) \
                and (rect[1] + rect[3] > camera.pos.y and rect[1] < camera.pos.y + WORLD_SIZE[1]):
                screen.blit(t["img"], rect)


class ParticleManager:
    def __init__(self):
        self.particles = []

    def add(self, p):
        self.particles.append(p)

    def update(self, dt):
        for i, p in reversed(list(enumerate(self.particles))):
            p.update(dt)
            if p.is_dead() == True:
                del self.particles[i]

    def draw(self):
        for p in self.particles:
            p.draw()


class Particle:
    def __init__(self, x, y, color=(0,0,0)):
        self.pos = pg.Vector2(x, y)
        self.speed = random.randint(200, 400)
        self.radius = random.randint(4, 8)
        self.angle = math.radians(random.randint(0, 360))
        self.color = color
        self.lifespan = random.uniform(0.3, 1)
        self.counter = 0

    def is_dead(self):
        if self.counter > self.lifespan:
            return True

    def update(self, dt):
        self.pos.x += math.cos(self.angle) * self.speed * dt
        self.pos.y += math.sin(self.angle) * self.speed * dt
        self.counter += dt
        self.radius -= (self.radius / self.lifespan) * dt

    def draw(self):
        pg.draw.circle(screen, self.color, self.pos, self.radius)


class Bullet:
    radius = 10

    def __init__(self, x, y, angle, tag):
        self.pos = pg.Vector2(x, y)
        self.speed = 800
        self.angle = angle
        self.lifespan = 1
        self.counter = 0
        self.collided = False
        self.tag = tag
        self.colors = {
            "player": (128, 35, 255),
            "enemy": (0,0,0),
        }
        self.collision_obj = Circle(Vector(*self.pos), self.radius)

    def update(self, dt):
        self.pos.x += math.cos(self.angle) * self.speed * dt
        self.pos.y += math.sin(self.angle) * self.speed * dt
        self.counter += dt
        
        # Collision with the map
        self.collision_obj.pos.x = self.pos.x
        self.collision_obj.pos.y = self.pos.y
        if game.level_manager.current_map().poly_collide(self.collision_obj):
            self.collided = True

        # Collision with enemies
        for i, e in enumerate(game.enemy_manager.entities):
            if self.tag == "player" and collide(self.collision_obj, e.collision_obj):
                self.collided = True
                del game.enemy_manager.entities[i] # Delete entity

    def create_particles(self):
        for i in range(random.randint(5, 10)):
            game.particle_manager.add(Particle(*self.pos, self.colors[self.tag]))

    def is_dead(self):
        if self.collided or self.counter > self.lifespan:
            self.create_particles();
            return True

    def draw(self):
        pg.draw.circle(screen, self.colors[self.tag], self.pos, self.radius)


class Player:
    def __init__(self):
        spawn_p = game.level_manager.current_map().spawners["player"][0]
        self.pos = pg.Vector2(spawn_p[0], spawn_p[1])
        self.vel = pg.Vector2()
        self.max_vel = 260
        self.friction = 0.9
        self.mode = "move"

        # Length from the center
        self.aim_line_length = 50
        self.can_shoot = True
        self.shoot_counter = 0
        self.angle = 0

        # Sprites & Animation
        self.img_path = "/characters/player.png"
        self.img = pg.image.load(rs_dir + self.img_path).convert_alpha()
        self.img_w, self.img_h = 64, 64

        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj = Circle(Vector(*self.c_pos), self.img_w/2)

    def shoot(self):
        if self.can_shoot:
            game.particle_manager.add(Bullet(*self.c_pos, self.angle, "player"))
            # Set kickback velocity (opposite to the bullet's velocity)
            self.vel.x -= math.cos(self.angle) * self.max_vel
            self.vel.y -= math.sin(self.angle) * self.max_vel
            self.can_shoot = False

    def move(self, dt):
        # Player collision and movement
        dx = self.vel.x * dt
        dy = self.vel.y * dt

        self.pos.x += dx
        self.pos.y += dy

        # Update collision object
        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj.pos = Vector(*self.c_pos)

        all_collisions = game.level_manager.current_map().poly_collide(self.collision_obj, capture_all=True)
        if all_collisions:
            for c in all_collisions:
                self.pos.x -= c.x
                self.pos.y -= c.y
                self.c_pos = center(*self.pos, self.img_w, self.img_h)
                self.collision_obj.pos = Vector(*self.c_pos)
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

    def update(self, dt):
        # Update shoot counter
        if not self.can_shoot:
            self.shoot_counter += dt
            if self.shoot_counter > 0.5:
                self.can_shoot = True
                self.shoot_counter = 0

        # Set initial velocities on keypress
        keys = pg.key.get_pressed()

        if self.can_shoot:
            # Reduce the global game speed by 3/4 when in aiming mode
            if keys[pg.K_SPACE]:
                game.change_speed(0.25)
                self.mode = "aim"
            elif self.mode == "aim": # If key is just released and the control mode hasn't changed
                game.change_speed(1)
                self.shoot()
                self.mode = "move"

        if self.mode == "move":
            if keys[pg.K_LEFT]:
                self.vel.x = -self.max_vel
            elif keys[pg.K_RIGHT]:
                self.vel.x = self.max_vel
            if keys[pg.K_UP]:
                self.vel.y = -self.max_vel
            elif keys[pg.K_DOWN]:
                self.vel.y = self.max_vel
        elif self.mode == "aim":
            # Aiming will not affected by the game speed
            if keys[pg.K_LEFT]:
                self.angle -= 5 * dt / game.speed
            elif keys[pg.K_RIGHT]:
                self.angle += 5 * dt / game.speed
            # Limit angle
            if self.angle < 0:
                self.angle = math.radians(360) + self.angle
            if self.angle > math.radians(360):
                self.angle = self.angle - math.radians(360)

        self.move(dt)
        camera.track((self.pos.x, self.pos.y, self.img_w, self.img_h))

    def draw(self):
        if self.mode == "aim":
            # Draw aiming lines
            end_pos = pg.Vector2(self.c_pos.x + math.cos(self.angle)*self.aim_line_length, self.c_pos.y + math.sin(self.angle)*self.aim_line_length)
            pg.draw.circle(screen, (128, 35, 255), end_pos, 5)

        # Draw self
        screen.blit(self.img, self.pos)


class EnemyManager:
    def __init__(self):
        self.detect_outside_FOV = False
        self.entities = []
        self.transparent_surface = pg.Surface(WORLD_SIZE, pg.SRCALPHA)

    def add(self, e):
        self.entities.append(e)

    def update(self, dt):
        for i, e in reversed(list(enumerate(self.entities))):
            e.update(dt, self.detect_outside_FOV)
            if e.is_dead() == True:
                del self.entities[i]

    def draw(self):
        # Draw transparent surface
        screen.blit(self.transparent_surface, (0,0))
        self.transparent_surface.fill((255,255,255,0))

        # Draw enemies
        for e in self.entities:
            e.draw()


class Enemy:
    def __init__(self, x, y):
        self.pos = pg.Vector2(x, y)
        self.vel = pg.Vector2()
        self.max_vel = random.randint(200, 300)
        self.friction = 0.9
        self.mode = "move"

        # Length from the center
        self.aim_line_length = 50
        self.can_shoot = False
        self.shoot_counter = 0
        self.angle = 0

        # Sprites & Animation
        self.img_path = "/characters/enemy.png"
        self.img = pg.image.load(rs_dir + self.img_path).convert_alpha()
        self.img_w, self.img_h = 64, 64

        # Field of view
        v = Vector
        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj = Circle(v(*self.c_pos), self.img_w/2)
        self.angular_vel = 0
        self.FOV_points = [
            v(-self.img_w/2, 0),
            v(self.img_w/2, 0), 
            v(self.img_w*2, self.img_h*5), 
            v(-self.img_w*2, self.img_h*5), 
        ]
        self.FOV_obj = Poly(v(*self.c_pos), self.FOV_points, self.angle)
        # How long between each random turn in idle mode
        self.turn_delay_timer = random.uniform(0.5,2)

        self.trigger_lockdown_timer = 5

    def is_dead(self):
        pass

    def move(self, dt):
        dx = self.vel.x * dt
        dy = self.vel.y * dt

        self.pos.x += dx
        self.pos.y += dy

        # Update collision object
        self.c_pos = center(*self.pos, self.img_w, self.img_h)
        self.collision_obj.pos = Vector(*self.c_pos)

        all_collisions = self.peer_collide() + game.level_manager.current_map().poly_collide( self.collision_obj, capture_all=True)
        if all_collisions:
            for c in all_collisions:
                self.pos.x -= c.x
                self.pos.y -= c.y
                self.c_pos = center(*self.pos, self.img_w, self.img_h)
                self.collision_obj.pos = Vector(*self.c_pos)
                # pass
            self.vel.x = 0
            self.vel.y = 0

        # Turn enemy
        self.FOV_obj.angle += self.angular_vel * dt

        # Decrease velocity
        self.vel.x *= self.friction
        self.vel.y *= self.friction
        self.angular_vel *= self.friction

        # Set velocity to 0 if too small
        if abs(self.vel.x) < 0.05:
            self.vel.x = 0
        if abs(self.vel.y) < 0.05:
            self.vel.y = 0

    def shoot(self):
        if self.can_shoot:
            game.particle_manager.add(Bullet(*self.c_pos, self.angle, "enemy"))
            # Set kickback velocity (opposite to the bullet's velocity)
            self.vel.x -= math.cos(self.angle) * self.max_vel
            self.vel.y -= math.sin(self.angle) * self.max_vel
            self.can_shoot = False

    def simulate_controls(self, dt, detect_outside_FOV):
        player = game.player
        dv = player.c_pos - self.c_pos
        
        if detect_outside_FOV or (collide(game.player.collision_obj, self.FOV_obj) or (abs(dv.x) < self.img_w and abs(dv.y) < self.img_h)):
            if not game.level_manager.lockdown:
                # Initiate lockdown after a few seconds delay
                self.trigger_lockdown_timer -= dt
                if self.trigger_lockdown_timer < 0:
                    game.level_manager.lockdown = True
                    self.trigger_lockdown_timer = 5

            # Set angular velocity
            # https://stackoverflow.com/questions/42258637/how-to-know-the-angle-between-two-vectors
            angle = math.atan2(self.c_pos.y-player.c_pos.y, self.c_pos.x-player.c_pos.x)
            rotated_angle = angle + math.radians(90)
            self.angle = angle + math.radians(180)
            a_diff = rotated_angle - self.FOV_obj.angle

            # Find the difference between two angles with sign
            # https://stackoverflow.com/questions/1878907/how-can-i-find-the-difference-between-two-angles
            da = math.atan2(math.sin(a_diff), math.cos(a_diff))
            self.angular_vel += da

            # Shoot
            # Only shoot if player is in direct line of sight
            v = Vector

            # Calculate how far the player is from the enemy
            l_diff = abs((v(*player.c_pos) - v(*self.c_pos)).ln())

            # Check for of the the player in the enemy's direct Line Of Sight
            LOS_poly_points = [
                v(-Bullet.radius, 0),
                v(Bullet.radius, 0),
                v(Bullet.radius, l_diff),
                v(-Bullet.radius, l_diff),
            ]
            LOS_poly = Poly(v(*self.c_pos), LOS_poly_points, rotated_angle)
            collision = game.level_manager.current_map().poly_collide(LOS_poly)
            # Shoot if there's not obstables in the way
            if not collision:
                self.shoot()

            # Debug, draw aiming line
            # pg.draw.polygon(screen, (100,100,100, 32), LOS_poly.points)

            # Update shoot counter here so the enemy doesn't immediately shoot when it detects the player
            if not self.can_shoot:
                self.shoot_counter += dt
                if self.shoot_counter > 1:
                    self.can_shoot = True
                    self.shoot_counter = 0

            # Move the enemy
            self.vel = dv
            if self.vel.x > self.max_vel:
                self.vel.x = self.max_vel
            elif self.vel.x < -self.max_vel:
                self.vel.x = -self.max_vel
            if self.vel.y > self.max_vel:
                self.vel.y = self.max_vel
            elif self.vel.y < -self.max_vel:
                self.vel.y = -self.max_vel
        else:
            # Turn the enemy randomly when not chasing the player (in idle mode)
            self.turn_delay_timer -= dt
            if abs(self.angular_vel) < 2 and self.turn_delay_timer < 0:
                self.turn_delay_timer = random.uniform(0.5, 2)
                self.angular_vel += random.uniform(-12,12) # Doesn't have to be in radians

    def peer_collide(self):
        all_collisions = []
        for e in game.enemy_manager.entities:
            if e != self:
                r = Response()
                if collide(self.collision_obj, e.collision_obj, r):
                    all_collisions.append(r.overlap_v)
        return all_collisions

    def update(self, dt, detect_outside_FOV):
        self.simulate_controls(dt, detect_outside_FOV)
        self.move(dt)
        self.FOV_obj.pos = Vector(*self.c_pos)

    def draw(self):
        if self.mode == "aim":
            # Draw aiming lines
            end_pos = pg.Vector2(self.c_pos.x + math.cos(self.angle)*self.aim_line_length, self.c_pos.y + math.sin(self.angle)*self.aim_line_length)
            pg.draw.circle(screen, (128, 35, 255), end_pos, 5)

        # Draw FOV area
        pg.draw.polygon(game.enemy_manager.transparent_surface, (0, 0, 0, 32), self.FOV_obj.points)

        # Draw self
        screen.blit(self.img, self.pos)


class LevelManager:
    def __init__(self, n=0):
        self.lockdown = False
        self.lockdown_timer = math.pi * 10 # 31.415 seconds
        self.lockdown_opacity_counter = 0
        self.current_level = n
        self.levels = [TiledMap("/tilemap.json")]
        self.transparent_surface = pg.Surface(WORLD_SIZE, pg.SRCALPHA)

    def current_map(self):
        return self.levels[self.current_level]

    def switch(self, n):
        self.current_level = n
        self.load_level(n)

    def load_level(self, n):
        # Spawn enemies
        spawn_p = self.current_map().spawners["enemy"]
        for p in spawn_p:
            game.enemy_manager.add(Enemy(p[0], p[1]))

    def update(self, dt):
        if self.lockdown:
            game.enemy_manager.detect_outside_FOV = True
            self.lockdown_timer -= dt
            self.lockdown_opacity_counter += dt
            if self.lockdown_timer < 0:
                # Code here to show restart menu
                self.lockdown = False
                self.lockdown_timer = math.pi * 10
                self.lockdown_opacity_counter = 0

    def draw_lockdown_filter(self):
        # Draw transparent red filter
        if self.lockdown:
            # Opacity ust be between 0 - 255
            opacity = 50 + math.sin(self.lockdown_opacity_counter * 4) * 50
            screen.blit(self.transparent_surface, (0,0))
            self.transparent_surface.fill((255,255,255,0))
            size = window.get_rect().size
            pg.draw.rect(self.transparent_surface, (255, 0, 76, opacity), (camera.pos.x-20, camera.pos.y-20, size[0]+40, size[1]+40))

    def draw(self):
        self.current_map().draw()


class GameManager:
    def __init__(self):
        self.prev_mode = MODE
        self.target_speed = 1
        self.speed = 1

    def setup(self):
        self.splash_screen = SplashScreen()
        self.level_manager = LevelManager()
        self.player = Player()
        self.enemy_manager = EnemyManager()
        self.particle_manager = ParticleManager()

        # Load level
        self.level_manager.load_level(0)

    def change_speed(self, speed):
        self.target_speed = speed

    def update(self, dt):
        ds = self.target_speed - self.speed # Delta speed
        self.speed += ds * 4 * dt # Increase the constant to increase the speed change
        dt *= self.speed # Change global game speed
        mode_changed = False
        if self.prev_mode != MODE:
            mode_changed = True
        if MODE == "splash":
            self.splash_screen.update(dt)
        if MODE == "menu":
            pass
        if MODE == "main":
            self.level_manager.update(dt)
            self.player.update(dt)
            self.enemy_manager.update(dt)
            self.particle_manager.update(dt)
        self.prev_mode = MODE

    def draw(self):
        if MODE == "splash":
            self.splash_screen.draw()
        if MODE == "main":
            self.level_manager.draw()
            self.player.draw()
            self.enemy_manager.draw()
            self.particle_manager.draw()

            # Top layers
            self.level_manager.draw_lockdown_filter()


####################
# Game Loop
####################


game = GameManager()
game.setup()
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
    
    dt = clock.tick(60)
    # fps debug
    fps = round(1000/dt)
    if fps < 40:
        print(fps, "fps (Low)")
    dt /= 1000

    window_size = window.get_rect().size
    screen_size = screen.get_rect().size

    camera.update(dt, window_size)
    game.update(dt)
    screen.fill(BG_COLOR)
    game.draw()
    # Render main surface after scaling it by the scale factor
    window.fill(BG_COLOR)
    window.blit(
        pg.transform.scale(screen, (int(screen_size[0]*camera.scale.x), int(screen_size[1]*camera.scale.y))), 
        (0, 0), 
        (camera.pos.x*camera.scale.x, camera.pos.y*camera.scale.x, window.get_width(), window.get_height())
    )
    pg.display.flip()